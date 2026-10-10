"""
Model for flow cytometry measurements on plant, animal, microbial or mycological samples.
"""
from __future__ import annotations

from invenio_i18n import lazy_gettext as _
from oarepo_communities.model.presets import communities_preset
from oarepo_model.api import model
from oarepo_model.customizations import AddMetadataExport
from oarepo_model.customizations.high_level.add_service_component import (
    AddServiceComponent,
)
from oarepo_model.datatypes.registry import from_yaml
from oarepo_rdm.model.presets import rdm_complete_preset
from oarepo_requests.model.presets.requests import requests_preset
from oarepo_workflows.model.presets import workflows_preset

from .serializers import DataCiteJSONSerializer
from .service_components import MeasurerNameCompatComponent

# TODO: Consider letting users add an image/icon for the model,
# so that the deposit model selection page is more visually appealing.
cytometry_model = model(
    "cytometry",
    version="1.0.0",
    description="Model for flow cytometry measurements on plant, animal, microbial or mycological samples.",
    presets=[
        rdm_complete_preset,
        # Official OARepo presets for community deposit + review + publish requests.
        # Keep these in the model before the first ``services setup`` / ``db create``.
        # See: https://github.com/oarepo/oarepo-workflows
        #      https://github.com/oarepo/oarepo-communities
        #      https://github.com/oarepo/oarepo-requests
        workflows_preset,
        communities_preset,
        requests_preset,
    ],
    types=[
        from_yaml("metadata.yaml", __file__)
    ],
    metadata_type="Metadata",
    customizations=[
        # Add your customizations here, such as custom exports and class mixins. 
        # The list of available extensions is at https://github.com/oarepo/oarepo-model.
        # If you do not find a customization that suits your needs or need a
        # help with using customizations, please contact us at support@cesnet.cz and
        # specify the keyword "Invenio repository development" inside the subject or
        # mail body of the request.

        # export for datacite
        AddMetadataExport(
            code="datacite",
            name=_("Datacite export"),
            mimetype="application/vnd.datacite.datacite+json",
            serializer=DataCiteJSONSerializer()
        ),
        AddServiceComponent(MeasurerNameCompatComponent),
    ],
    configuration={
        "ui_blueprint_name": "cytometry_ui"
    }
)
