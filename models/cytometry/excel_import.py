"""Import cytometry JSON Lines (schema 0.2) as deposit drafts.

Pipeline:
1. Convert Excel → JSONL with ``python -m models.cytometry.excel_to_json``.
2. Import JSONL → drafts with this module (files resolved by ``file_names``).

Each JSONL line is one measurement record matching
``docs_cesnet/flow_cytometry_schema_v0.2.json``. Domain sections are stored
under ``metadata``; ``file_names`` become draft file uploads; ``ark`` / ``doi``
are kept only as informational identifiers when present.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

RESOURCE_TYPE_ID = "datasets"

LICENSE_ALIASES = {
    "cc-by-4.0": "4-BY",
    "cc-by": "4-BY",
    "CC-BY-4.0": "4-BY",
}
LANGUAGE_ALIASES = {
    "eng": "en",
    "en": "en",
    "cze": "cs",
    "ces": "cs",
    "cs": "cs",
}

DOMAIN_KEYS = (
    "project_info",
    "sample_provenance",
    "preparation_and_standard",
    "instrumentation",
    "measurement",
)


@dataclass
class ImportGroup:
    """One JSONL record ready to become a draft (or carrying errors)."""

    line_number: int
    label: str
    payload: dict[str, Any] | None = None
    files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def compact(value: Any) -> Any:
    """Drop None / empty containers recursively while keeping False/0."""
    if isinstance(value, dict):
        cleaned = {key: compact(item) for key, item in value.items()}
        return {key: item for key, item in cleaned.items() if item is not None and item != []}
    if isinstance(value, list):
        return [compact(item) for item in value if item is not None and item != {}]
    return value


def person_from_name(fullname: str) -> dict[str, Any]:
    """Build an RDM creator from a bare full name."""
    name = fullname.strip()
    if "," in name:
        family, given = [part.strip() for part in name.split(",", 1)]
        return {
            "person_or_org": {
                "type": "personal",
                "family_name": family,
                "given_name": given,
                "name": f"{family}, {given}".strip(", "),
            }
        }
    parts = name.split()
    if len(parts) >= 2:
        given = " ".join(parts[:-1])
        family = parts[-1]
        return {
            "person_or_org": {
                "type": "personal",
                "family_name": family,
                "given_name": given,
                "name": f"{family}, {given}",
            }
        }
    return {
        "person_or_org": {
            "type": "personal",
            "family_name": name,
            "name": name,
        }
    }


def creators_from_authors(authors: Any) -> list[dict[str, Any]]:
    """Map schema Person authors onto RDM creators."""
    creators: list[dict[str, Any]] = []
    if not isinstance(authors, list):
        return creators
    for author in authors:
        if isinstance(author, dict) and author.get("fullname"):
            creator = person_from_name(str(author["fullname"]))
            orcid = author.get("orcid")
            if orcid:
                creator["person_or_org"]["identifiers"] = [
                    {"scheme": "orcid", "identifier": str(orcid)}
                ]
            affiliation = author.get("affiliation")
            if affiliation:
                creator["affiliations"] = [{"name": str(affiliation)}]
            creators.append(creator)
        elif isinstance(author, str) and author.strip():
            creators.append(person_from_name(author))
    return creators


def build_title(record: dict[str, Any]) -> str:
    """Compose a deposit title from taxa / specimen / measurement date."""
    taxa = (record.get("sample_provenance") or {}).get("taxon") or []
    names = [
        taxon.get("scientific_name")
        for taxon in taxa
        if isinstance(taxon, dict) and taxon.get("scientific_name")
    ]
    specimen = (record.get("sample_provenance") or {}).get("specimen_id")
    sample_number = (record.get("sample_provenance") or {}).get("sample_number")
    measurement_date = (record.get("measurement") or {}).get("measurement_date")
    parts = []
    if names:
        parts.append(", ".join(names))
    if specimen:
        parts.append(str(specimen))
    elif sample_number:
        parts.append(str(sample_number))
    if measurement_date:
        parts.append(str(measurement_date))
    return " — ".join(parts) if parts else "Flow cytometry measurement"


def resolve_license(value: str) -> str:
    """Map a CLI license alias onto the rights vocabulary id."""
    return LICENSE_ALIASES.get(value, value)


def resolve_language(value: str) -> str:
    """Map a CLI language alias onto the languages vocabulary id."""
    return LANGUAGE_ALIASES.get(value, value)


def check_filename(
    name: str, files_dir: Path, line_number: int
) -> tuple[Path | None, str | None]:
    """Resolve a file_names entry against ``files_dir``."""
    if not name or not str(name).strip():
        return None, f"řádek {line_number}: prázdný název souboru"
    path = files_dir / str(name).strip()
    if not path.is_file():
        return None, f"řádek {line_number}: soubor '{name}' ve složce {files_dir} neexistuje"
    return path, None


def record_to_payload(
    record: dict[str, Any],
    *,
    line_number: int,
    files_dir: Path,
    license_id: str,
    language_id: str,
    community: str | None,
) -> ImportGroup:
    """Wrap one domain record as an Invenio draft payload."""
    label = (
        (record.get("sample_provenance") or {}).get("sample_number")
        or (record.get("sample_provenance") or {}).get("specimen_id")
        or (record.get("ark") or f"line-{line_number}")
    )
    errors: list[str] = []

    file_names = record.get("file_names") or []
    if not isinstance(file_names, list) or not file_names:
        errors.append(f"řádek {line_number}: chybí file_names")

    files: list[Path] = []
    seen: set[str] = set()
    for name in file_names if isinstance(file_names, list) else []:
        key = str(name).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        path, error = check_filename(key, files_dir, line_number)
        if error:
            errors.append(error)
        elif path is not None:
            files.append(path)

    authors = (record.get("project_info") or {}).get("authors") or []
    creators = creators_from_authors(authors)
    if not creators:
        errors.append(
            f"řádek {line_number}: bez autorů projektu nejde vyplnit tvůrce záznamu"
        )

    measurement_date = (record.get("measurement") or {}).get("measurement_date")
    publication_date = measurement_date or date.today().isoformat()

    metadata: dict[str, Any] = {
        "title": build_title(record),
        "resource_type": {"id": RESOURCE_TYPE_ID},
        "publication_date": publication_date,
        "creators": creators,
        "languages": [{"id": language_id}],
        "rights": [{"id": license_id}],
    }
    for key in DOMAIN_KEYS:
        if key in record and record[key] is not None:
            metadata[key] = record[key]

    payload: dict[str, Any] = {
        "metadata": compact(metadata),
        "files": {"enabled": True},
    }
    if community:
        payload["parent"] = {"communities": {"default": {"id": community}}}

    return ImportGroup(
        line_number=line_number,
        label=str(label),
        payload=None if errors else payload,
        files=files,
        errors=errors,
    )


def load_jsonl_groups(
    jsonl_path: Path,
    files_dir: Path,
    *,
    license_id: str,
    language_id: str,
    community: str | None,
) -> tuple[list[ImportGroup], list[str]]:
    """Parse JSONL into import groups."""
    groups: list[ImportGroup] = []
    workbook_errors: list[str] = []
    if not jsonl_path.is_file():
        return [], [f"Soubor {jsonl_path} neexistuje."]

    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            text = raw.strip()
            if not text:
                continue
            try:
                record = json.loads(text)
            except json.JSONDecodeError as exc:
                groups.append(
                    ImportGroup(
                        line_number=line_number,
                        label=f"line-{line_number}",
                        errors=[f"řádek {line_number}: neplatný JSON ({exc})"],
                    )
                )
                continue
            if not isinstance(record, dict):
                groups.append(
                    ImportGroup(
                        line_number=line_number,
                        label=f"line-{line_number}",
                        errors=[f"řádek {line_number}: očekává se JSON objekt"],
                    )
                )
                continue
            groups.append(
                record_to_payload(
                    record,
                    line_number=line_number,
                    files_dir=files_dir,
                    license_id=license_id,
                    language_id=language_id,
                    community=community,
                )
            )

    if not groups and not workbook_errors:
        workbook_errors.append("JSONL neobsahuje žádný záznam.")
    return groups, workbook_errors


def report(groups: list[ImportGroup], workbook_errors: list[str]) -> str:
    """Human-readable dry-run report."""
    lines: list[str] = []
    errors = list(workbook_errors)
    for group in groups:
        errors.extend(group.errors)
    if errors:
        lines.append("Chyby:")
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    for group in groups:
        if group.errors or not group.payload:
            continue
        lines.append(f"{group.label} (JSONL řádek {group.line_number})")
        file_names = ", ".join(path.name for path in group.files) or "(žádné)"
        lines.append(f"Soubory: {file_names}")
        lines.append(json.dumps(group.payload, ensure_ascii=False, indent=2))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def identity_for_user(identifier: str):
    """Build an identity that can create a draft as the given user."""
    from invenio_access.permissions import any_user, authenticated_user
    from invenio_access.utils import get_identity
    from invenio_accounts.proxies import current_datastore

    user = current_datastore.get_user(identifier)
    if user is None:
        user = current_datastore.find_user(username=identifier)
    if user is None:
        user = current_datastore.find_user(email=identifier)
    if user is None:
        raise SystemExit(f"Uživatel „{identifier}“ v Inveniu neexistuje.")
    identity = get_identity(user)
    identity.provides.add(authenticated_user)
    identity.provides.add(any_user)
    return identity


def create_drafts(groups: list[ImportGroup], user: str) -> list[str]:
    """Create one draft per valid group and attach its files. Returns draft ids."""
    from invenio_app.factory import create_app
    from oarepo_runtime.proxies import current_runtime

    app = create_app()
    draft_ids: list[str] = []
    with app.app_context():
        identity = identity_for_user(user)
        model = current_runtime.models["cytometry"]
        service = model.service
        files_service = model.draft_file_service
        if files_service is None:
            raise SystemExit("Model cytometry nemá službu pro soubory draftu.")
        for group in groups:
            if group.payload is None:
                continue
            try:
                item = service.create(identity, group.payload)
            except Exception as exc:
                raise SystemExit(
                    f"{group.label}: záznam se nepodařilo založit ({exc})"
                ) from exc
            draft_id = item.id
            if group.files:
                files_service.init_files(
                    identity,
                    draft_id,
                    [{"key": path.name} for path in group.files],
                )
                for path in group.files:
                    with path.open("rb") as stream:
                        files_service.set_file_content(
                            identity,
                            draft_id,
                            path.name,
                            stream,
                            path.stat().st_size,
                        )
                    files_service.commit_file(identity, draft_id, path.name)
            draft_ids.append(draft_id)
            print(f"{group.label}: draft {draft_id}  /cytometry/uploads/{draft_id}")
    return draft_ids


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Command line of the importer."""
    parser = argparse.ArgumentParser(
        description=(
            "Naimportuje JSONL dávku cytometrie (schema 0.2) jako drafty záznamů."
        ),
    )
    parser.add_argument(
        "jsonl",
        nargs="?",
        type=Path,
        help="Soubor .jsonl ze skriptu excel_to_json",
    )
    parser.add_argument(
        "--files-dir",
        type=Path,
        help="Složka s FCS a dalšími přílohami. Názvy musí odpovídat file_names.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Jen sestaví záznamy a vypíše chyby. Nic nezakládá.",
    )
    parser.add_argument(
        "--user",
        help="E-mail nebo uživatelské jméno vlastníka draftů.",
    )
    parser.add_argument(
        "--license",
        default="cc-by-4.0",
        help="Id licence ve slovníku práv, nebo alias cc-by-4.0 (= 4-BY).",
    )
    parser.add_argument(
        "--language",
        default="eng",
        help="Id jazyka ve slovníku, nebo alias eng (= en).",
    )
    parser.add_argument(
        "--community",
        help="Slug komunity. Bez něj vznikne individuální draft.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run a dry-run or create drafts. Returns a process status code."""
    args = parse_args(argv)
    if args.jsonl is None or args.files_dir is None:
        print("Zadejte JSONL soubor a --files-dir.", file=sys.stderr)
        return 2
    if not args.jsonl.is_file():
        print(f"Soubor {args.jsonl} neexistuje.", file=sys.stderr)
        return 2
    if not args.files_dir.is_dir():
        print(f"Složka {args.files_dir} neexistuje.", file=sys.stderr)
        return 2
    if not args.dry_run and not args.user:
        print("Ostrý import potřebuje --user.", file=sys.stderr)
        return 2

    license_id = resolve_license(args.license)
    language_id = resolve_language(args.language)
    groups, workbook_errors = load_jsonl_groups(
        args.jsonl,
        args.files_dir,
        license_id=license_id,
        language_id=language_id,
        community=args.community,
    )
    print(
        f"Nastavení: licence {license_id}, jazyk {language_id}, "
        f"komunita {args.community or '(žádná)'}"
    )
    print(report(groups, workbook_errors), end="")
    failed = bool(workbook_errors) or any(group.errors for group in groups)
    if failed:
        return 1
    if args.dry_run:
        return 0
    create_drafts(groups, args.user)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
