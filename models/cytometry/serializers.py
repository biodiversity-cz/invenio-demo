from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from invenio_rdm_records.resources.serializers.datacite.schema import (
    DataCite43Schema as DataCiteSchema,
)


class DataCiteJSONSerializer(MarshmallowSerializer):
    """Marshmallow based DataCite serializer for cytometry records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DataCiteSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={},
            **options,
        )

    def dump_obj(self, obj, **kwargs):
        """Serialize one record and enrich with selected cytometry fields."""
        data = super().dump_obj(obj, **kwargs)
        metadata = (obj or {}).get("metadata") or {}
        if not isinstance(data, dict):
            return data

        descriptions = list(data.get("descriptions") or [])
        project = metadata.get("project_info") or {}
        if project.get("project_description"):
            descriptions.append(
                {
                    "description": project["project_description"],
                    "descriptionType": "Abstract",
                }
            )

        measurement = metadata.get("measurement") or {}
        if measurement.get("purpose"):
            descriptions.append(
                {
                    "description": measurement["purpose"],
                    "descriptionType": "Methods",
                }
            )
        if measurement.get("interpretation_notes"):
            descriptions.append(
                {
                    "description": measurement["interpretation_notes"],
                    "descriptionType": "Other",
                }
            )
        if descriptions:
            data["descriptions"] = descriptions

        location = (metadata.get("sample_provenance") or {}).get("location") or {}
        place_parts = [
            location.get("locality_description"),
            location.get("country_or_region"),
            location.get("coordinates"),
        ]
        place = ", ".join(part for part in place_parts if part)
        if place:
            data["geoLocations"] = [{"geoLocationPlace": place}]

        subjects = list(data.get("subjects") or [])
        for taxon in (metadata.get("sample_provenance") or {}).get("taxon") or []:
            name = taxon.get("scientific_name") if isinstance(taxon, dict) else None
            if name:
                subjects.append({"subject": name})
        fluorochrome = (metadata.get("preparation_and_standard") or {}).get(
            "fluorochrome"
        )
        if fluorochrome:
            subjects.append({"subject": f"fluorochrome: {fluorochrome}"})
        if subjects:
            data["subjects"] = subjects

        return data
