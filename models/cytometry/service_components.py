"""Cytometry record service components."""

from __future__ import annotations

from invenio_drafts_resources.services.records.components import ServiceComponent

from .metadata_compat import normalize_measurer_name_in_record


class MeasurerNameCompatComponent(ServiceComponent):
    """Coerce legacy string measurer_name to array before schema validation."""

    def edit(self, identity, draft=None, record=None, **kwargs):
        if draft is not None:
            normalize_measurer_name_in_record(draft)

    def new_version(self, identity, draft=None, record=None, **kwargs):
        if draft is not None:
            normalize_measurer_name_in_record(draft)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        if record is not None:
            normalize_measurer_name_in_record(record)

    def create(self, identity, data=None, record=None, **kwargs):
        if record is not None:
            normalize_measurer_name_in_record(record)
