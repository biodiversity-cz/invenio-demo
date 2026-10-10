"""Backward compatibility for cytometry metadata shape changes."""

from __future__ import annotations

from typing import Any


def normalize_measurer_name(value: Any) -> list[str]:
    """Match deposit UI: string or char-split array → list of names."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        trimmed = value.strip()
        return [trimmed] if trimmed else []
    if not isinstance(value, list):
        return []
    if (
        len(value) > 1
        and all(isinstance(item, str) and len(item) <= 1 for item in value)
    ):
        joined = "".join(value).strip()
        return [joined] if joined else []
    return [
        item.strip()
        for item in value
        if isinstance(item, str) and item.strip()
    ]


def normalize_measurer_name_in_record(record) -> None:
    """In-place fix of metadata.measurement.measurer_name on a record/draft."""
    metadata = record.get("metadata")
    if not metadata:
        return
    measurement = metadata.get("measurement")
    if not measurement:
        return
    current = measurement.get("measurer_name")
    normalized = normalize_measurer_name(current)
    if current != normalized:
        measurement["measurer_name"] = normalized
