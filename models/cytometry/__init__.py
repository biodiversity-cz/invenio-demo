"""Model for cytometry.

This package contains the model definition for cytometry.
To change model's metadata, edit the metadata.yaml file.
To change presets, add serialization/deserialization formats
and similar operations please see the model.py file.
"""

from __future__ import annotations

from .model import cytometry_model

__all__ = ( "cytometry_model", )