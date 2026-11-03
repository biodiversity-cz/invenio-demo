#!/usr/bin/env python3
"""Convert the cytometry Import_Data workbook (schema 0.2) to JSON Lines.

Performs whitespace trimming, decimal-comma handling, GPS normalization to
WGS84 floats, positional consistency checks for semicolon-separated object
arrays, and validation against the JSON Schema 0.2 contract.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import openpyxl
from jsonschema import ValidationError, validate

DEFAULT_SCHEMA = Path(__file__).resolve().parents[3] / "docs_cesnet" / "flow_cytometry_schema_v0.2.json"
DEFAULT_EXCEL = Path(__file__).resolve().parents[3] / "docs_cesnet" / "invenio_flow_cytometry_import_v0.2.xlsx"


def _is_missing(val):
    """True for None / NaN / blank Excel cells."""
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False


def parse_list(val):
    """Split a semicolon-separated cell and strip whitespace."""
    if _is_missing(val):
        return []
    s_val = str(val).strip()
    if not s_val or s_val.lower() in ["none", "nan"]:
        return []
    return [p.strip() for p in s_val.split(";")]


def clean_val(val, val_type="string"):
    """Cast a cell value; treat null/none/nan as missing."""
    if _is_missing(val):
        return None
    s_val = str(val).strip()
    if not s_val or s_val.lower() in ["null", "none", "nan"]:
        return None

    if val_type == "string":
        return s_val
    if val_type == "float":
        try:
            return float(s_val.replace(",", "."))
        except ValueError:
            return None
    if val_type == "int":
        try:
            return int(float(s_val.replace(",", ".")))
        except ValueError:
            return None
    if val_type == "bool":
        if s_val.upper() in ["TRUE", "1", "YES", "ANO"]:
            return True
        if s_val.upper() in ["FALSE", "0", "NO", "NE"]:
            return False
        return None
    return s_val


def parse_coordinate(val):
    """Normalize a GPS cell to a WGS84 decimal-degree float."""
    if _is_missing(val):
        return None
    s_val = str(val).strip()
    if not s_val or s_val.lower() in ["null", "none", "nan"]:
        return None

    direction = None
    dir_match = re.search(r"([NSEWnsew])", s_val)
    if dir_match:
        direction = dir_match.group(1).upper()
        s_val_clean = re.sub(r"[NSEWnsew]", "", s_val).strip()
    else:
        s_val_clean = s_val

    s_val_clean = (
        s_val_clean.replace("°", " ")
        .replace("'", " ")
        .replace('"', " ")
        .replace(",", ".")
    )
    parts = s_val_clean.split()

    if len(parts) == 1:
        try:
            num = float(parts[0])
            if direction in ["S", "W"]:
                num = -abs(num)
            elif direction in ["N", "E"]:
                num = abs(num)
            return round(num, 7)
        except ValueError:
            pass

    try:
        nums = []
        for part in parts:
            try:
                nums.append(float(part))
            except ValueError:
                pass

        if len(nums) == 3:
            deg, mn, sec = nums
            num = abs(deg) + (mn / 60.0) + (sec / 3600.0)
            if deg < 0 or "-" in s_val:
                num = -num
        elif len(nums) == 2:
            deg, mn = nums
            num = abs(deg) + (mn / 60.0)
            if deg < 0 or "-" in s_val:
                num = -num
        elif len(nums) == 1:
            num = nums[0]
        else:
            return None

        if direction in ["S", "W"]:
            num = -abs(num)
        elif direction in ["N", "E"]:
            num = abs(num)
        return round(num, 7)
    except Exception:
        return None


def parse_object_array(row_dict, field_specs):
    """Build an object array from aligned semicolon-separated columns."""
    parsed_columns = {}
    lengths = {}

    for prop, (col_name, val_type) in field_specs.items():
        items = parse_list(row_dict.get(col_name))
        parsed_columns[prop] = (items, val_type)
        if items:
            lengths[prop] = len(items)

    if not lengths:
        return []

    max_len = max(lengths.values())
    for prop, length in lengths.items():
        if length != max_len:
            raise ValueError(
                f"Nesouhlasí počet prvků v poli pro '{prop}'. "
                f"Nalezeno {length} prvků vs maximum {max_len} v tomto řádku."
            )

    result_array = []
    for i in range(max_len):
        obj = {}
        for prop, (items, val_type) in parsed_columns.items():
            if i < len(items):
                cleaned = clean_val(items[i], val_type)
                if cleaned is not None:
                    obj[prop] = cleaned
        if obj:
            result_array.append(obj)
    return result_array


def build_person_list(fullname_str, orcid_str, affiliation_str=None):
    """Build a list of person objects from aligned semicolon columns."""
    fullnames = parse_list(fullname_str)
    orcids = parse_list(orcid_str)
    affiliations = parse_list(affiliation_str)

    persons = []
    count = max(len(fullnames), len(orcids), len(affiliations), 0)
    for i in range(count):
        fn = clean_val(fullnames[i], "string") if i < len(fullnames) else None
        orc = clean_val(orcids[i], "string") if i < len(orcids) else None
        aff = clean_val(affiliations[i], "string") if i < len(affiliations) else None
        if not (fn or orc or aff):
            continue
        person = {}
        if fn:
            person["fullname"] = fn
        if orc:
            person["orcid"] = orc
        if aff:
            person["affiliation"] = aff
        persons.append(person)
    return persons


def _date_only(val):
    cleaned = clean_val(val, "string")
    if cleaned is None:
        return None
    return str(cleaned).split(" ")[0]


def build_record(row_dict):
    """Map one Import_Data row dict onto a schema 0.2 record."""
    record = {}

    schema_ver = clean_val(row_dict.get("schema_version"), "string") or "0.2"
    ark = clean_val(row_dict.get("ark"), "string")
    doi = clean_val(row_dict.get("doi"), "string")
    file_names = parse_list(row_dict.get("file_names"))

    record["schema_version"] = schema_ver
    if ark:
        record["ark"] = ark
    if doi:
        record["doi"] = doi
    if file_names:
        record["file_names"] = file_names

    project_info = {}
    proj_title = clean_val(row_dict.get("project_info.project_title"), "string")
    proj_desc = clean_val(row_dict.get("project_info.project_description"), "string")
    pub_dois = parse_list(row_dict.get("project_info.publication_doi"))
    funding = clean_val(row_dict.get("project_info.funding"), "string")
    authors = build_person_list(
        row_dict.get("project_info.authors.fullname"),
        row_dict.get("project_info.authors.orcid"),
        row_dict.get("project_info.authors.affiliation"),
    )
    if proj_title:
        project_info["project_title"] = proj_title
    if proj_desc:
        project_info["project_description"] = proj_desc
    if pub_dois:
        project_info["publication_doi"] = pub_dois
    if funding:
        project_info["funding"] = funding
    if authors:
        project_info["authors"] = authors
    if project_info:
        record["project_info"] = project_info

    sample_prov = {}
    for key, col, kind in [
        ("specimen_id", "sample_provenance.specimen_id", "string"),
        ("sample_number", "sample_provenance.sample_number", "string"),
        ("material_type", "sample_provenance.material_type", "string"),
        ("organ", "sample_provenance.organ", "string"),
        ("collector_team", "sample_provenance.collector_team", "string"),
    ]:
        val = clean_val(row_dict.get(col), kind)
        if val is not None:
            sample_prov[key] = val

    ind_count = clean_val(row_dict.get("sample_provenance.individuals_count"), "int")
    sample_prov["individuals_count"] = 1 if ind_count is None else ind_count

    date_samp = _date_only(row_dict.get("sample_provenance.date_of_sampling"))
    if date_samp:
        sample_prov["date_of_sampling"] = date_samp

    taxa = parse_object_array(
        row_dict,
        {
            "scientific_name": ("sample_provenance.taxon.scientific_name", "string"),
            "strain_cultivar": ("sample_provenance.taxon.strain_cultivar", "string"),
            "col_id": ("sample_provenance.taxon.col_id", "string"),
            "notes": ("sample_provenance.taxon.notes", "string"),
        },
    )
    if taxa:
        sample_prov["taxon"] = taxa

    collectors = build_person_list(
        row_dict.get("sample_provenance.collector.fullname"),
        row_dict.get("sample_provenance.collector.orcid"),
        row_dict.get("sample_provenance.collector.affiliation"),
    )
    if collectors:
        sample_prov["collector"] = collectors

    location = {}
    country = clean_val(row_dict.get("sample_provenance.location.country_or_region"), "string")
    locality = clean_val(
        row_dict.get("sample_provenance.location.locality_description"), "string"
    )
    lat_val = parse_coordinate(row_dict.get("sample_provenance.location.latitude"))
    lon_val = parse_coordinate(row_dict.get("sample_provenance.location.longitude"))
    if country:
        location["country_or_region"] = country
    if locality:
        location["locality_description"] = locality
    if lat_val is not None:
        location["latitude"] = lat_val
    if lon_val is not None:
        location["longitude"] = lon_val
    if location:
        sample_prov["location"] = location

    vouchers = parse_object_array(
        row_dict,
        {
            "institution_code": ("sample_provenance.vouchers.institution_code", "string"),
            "catalog_number": ("sample_provenance.vouchers.catalog_number", "string"),
            "pid": ("sample_provenance.vouchers.pid", "string"),
        },
    )
    if vouchers:
        sample_prov["vouchers"] = vouchers
    if sample_prov:
        record["sample_provenance"] = sample_prov

    prep_std = {}
    for key, col, kind in [
        ("isolation_buffer", "preparation_and_standard.isolation_buffer", "string"),
        ("buffer_additives", "preparation_and_standard.buffer_additives", "string"),
        ("fluorochrome", "preparation_and_standard.fluorochrome", "string"),
        ("internal_standard_species", "preparation_and_standard.internal_standard_species", "string"),
        ("internal_standard_material", "preparation_and_standard.internal_standard_material", "string"),
        ("standard_c_value_pg", "preparation_and_standard.standard_c_value_pg", "float"),
        ("standard_c_value_citation", "preparation_and_standard.standard_c_value_citation", "string"),
    ]:
        val = clean_val(row_dict.get(col), kind)
        if val is not None:
            prep_std[key] = val
    if prep_std:
        record["preparation_and_standard"] = prep_std

    instr = {}
    for key, col in [
        ("instrument_affiliation", "instrumentation.instrument_affiliation"),
        ("manufacturer", "instrumentation.manufacturer"),
        ("model", "instrumentation.model"),
        ("instrument_id", "instrumentation.instrument_id"),
        ("light_source", "instrumentation.light_source"),
        ("channel_name_standard_position", "instrumentation.channel_name_standard_position"),
    ]:
        val = clean_val(row_dict.get(col), "string")
        if val is not None:
            instr[key] = val
    if instr:
        record["instrumentation"] = instr

    meas = {}
    measurers = build_person_list(
        row_dict.get("measurement.measurer.fullname"),
        row_dict.get("measurement.measurer.orcid"),
        row_dict.get("measurement.measurer.affiliation"),
    )
    if measurers:
        meas["measurer"] = measurers[0]

    m_date = _date_only(row_dict.get("measurement.measurement_date"))
    if m_date:
        meas["measurement_date"] = m_date

    purpose = clean_val(row_dict.get("measurement.purpose"), "string")
    if purpose:
        meas["purpose"] = purpose

    std_used = clean_val(row_dict.get("measurement.internal_standard_used"), "bool")
    if std_used is None:
        std_used = True
    meas["internal_standard_used"] = std_used

    if std_used:
        std_peak_pos = clean_val(row_dict.get("measurement.standard_peak_position"), "float")
        if std_peak_pos is not None:
            meas["standard_peak_position"] = std_peak_pos
    # When no internal standard: omit standard_peak_position entirely.

    sample_peaks = parse_object_array(
        row_dict,
        {
            "peak_position": ("measurement.sample_peaks.peak_position", "float"),
            "peak_sample_to_peak_standard": (
                "measurement.sample_peaks.peak_sample_to_peak_standard",
                "float",
            ),
            "peak_description": ("measurement.sample_peaks.peak_description", "string"),
        },
    )
    if not std_used:
        for peak in sample_peaks:
            peak.pop("peak_sample_to_peak_standard", None)
    if sample_peaks:
        meas["sample_peaks"] = sample_peaks

    interp = clean_val(row_dict.get("measurement.interpretation_notes"), "string")
    if interp:
        meas["interpretation_notes"] = interp

    if not std_used:
        # Species/details of a standard that was not used should not be required;
        # drop empty-looking leftover only when flag is false and species was blank
        # already handled by omission. If species was filled anyway, keep it.
        pass

    if meas:
        record["measurement"] = meas
    return record


def convert_excel_to_json(excel_path, schema_path, output_jsonl_path, errors_csv_path):
    """Convert Import_Data rows to validated JSON Lines."""
    with open(schema_path, "r", encoding="utf-8") as handle:
        schema = json.load(handle)

    wb = openpyxl.load_workbook(excel_path, data_only=True)
    if "Import_Data" not in wb.sheetnames:
        raise ValueError("Excel neobsahuje požadovaný list 'Import_Data'.")

    ws = wb["Import_Data"]
    headers = [ws.cell(row=2, column=col).value for col in range(1, ws.max_column + 1)]

    records = []
    errors = []

    for row_idx in range(4, ws.max_row + 1):
        row_values = [
            ws.cell(row=row_idx, column=col).value for col in range(1, ws.max_column + 1)
        ]
        if all(v is None or str(v).strip() == "" for v in row_values):
            continue

        row_dict = dict(zip(headers, row_values))
        record_id = (
            clean_val(row_dict.get("sample_provenance.sample_number"), "string")
            or clean_val(row_dict.get("sample_provenance.specimen_id"), "string")
            or f"Radek-{row_idx}"
        )

        try:
            record = build_record(row_dict)
            validate(instance=record, schema=schema)
            records.append(record)
        except ValidationError as ve:
            errors.append(
                {
                    "row_index": row_idx,
                    "specimen_id": record_id,
                    "error_type": "SchemaValidationError",
                    "detail": (
                        f"Cesta: {'.'.join(str(p) for p in ve.path)} | "
                        f"Zpráva: {ve.message}"
                    ),
                }
            )
        except Exception as exc:
            errors.append(
                {
                    "row_index": row_idx,
                    "specimen_id": record_id,
                    "error_type": exc.__class__.__name__,
                    "detail": str(exc),
                }
            )

    with open(output_jsonl_path, "w", encoding="utf-8") as out:
        for rec in records:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    if errors:
        with open(errors_csv_path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["row_index", "specimen_id", "error_type", "detail"],
            )
            writer.writeheader()
            writer.writerows(errors)
        print(
            f"UPOZORNĚNÍ: Nalezeno {len(errors)} chyb. "
            f"Protokol: '{errors_csv_path}'."
        )

    print(
        f"ÚSPĚCH: Zpracováno {len(records)} platných záznamů → '{output_jsonl_path}'."
    )
    return len(records), len(errors)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Konvertor Excelu (Import_Data) do Invenio JSON-Lines dle schématu 0.2."
    )
    parser.add_argument("--excel", default=str(DEFAULT_EXCEL), help="Cesta k Excel souboru")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Cesta k JSON schématu")
    parser.add_argument("--output", default="invenio_records.jsonl", help="Výstupní JSONL")
    parser.add_argument("--errors", default="import_errors.csv", help="CSV s chybami")
    args = parser.parse_args(argv)
    convert_excel_to_json(args.excel, args.schema, args.output, args.errors)


if __name__ == "__main__":
    main()
