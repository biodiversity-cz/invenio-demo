"""Invenio app hooks for the cytometry model."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def finalize_app(app: Flask) -> None:
    """Reserved hook; no runtime patching needed after the 0.2 schema cutover."""
    return
