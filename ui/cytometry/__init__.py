from oarepo_rdm.ui.config import RDMRecordsUIResourceConfig
from oarepo_rdm.ui.resource import RDMRecordsUIResource
from oarepo_ui.utils import can_view_deposit_page
from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _
from oarepo_ui.overrides import UIComponent
from oarepo_ui.overrides.components import UIComponentImportMode
from oarepo_ui.proxies import current_oarepo_ui

from .components.published_deposit_permissions import (
    PublishedDepositPermissionsComponent,
)


class CytometryUIResourceConfig(RDMRecordsUIResourceConfig):
    template_folder = "templates"
    url_prefix = "/cytometry"
    blueprint_name = "cytometry_ui"
    model_name = "cytometry"
    search_component = UIComponent(
        "CytometryResultsListItem",
        "@js/cytometry/search/ResultsListItem",
        UIComponentImportMode.DEFAULT
    )

    components = [
        *RDMRecordsUIResourceConfig.components,
        PublishedDepositPermissionsComponent,
    ]

    application_id = "cytometry"


class CytometryUIResource(RDMRecordsUIResource):
    pass

def ui_overrides(app):
    """Register UI overrides."""
    ui_resource_config = CytometryUIResourceConfig()

    if (
        current_oarepo_ui is not None
        and ui_resource_config.model
        and ui_resource_config.model.record_json_schema
        and ui_resource_config.search_component
    ):
        current_oarepo_ui.register_result_list_item(
            ui_resource_config.model.record_json_schema, ui_resource_config.search_component
        )


def init_menu(app):
    """Initialize menu before first request."""
    ui_resource_config = CytometryUIResourceConfig()

    with app.app_context():
        current_menu.submenu("plus.create_cytometry").register(
            f"{ui_resource_config.blueprint_name}.deposit_create",
            _("New Cytometry"),
            order=1,
            visible_when=can_view_deposit_page,
        )

def finalize_app(app):
    """Finalize app"""
    from models.cytometry.app_hooks import finalize_app as register_cytometry_services

    init_menu(app)
    ui_overrides(app)
    register_cytometry_services(app)

def create_blueprint(app):
    """Register blueprint for this resource."""
    blueprint = CytometryUIResource(CytometryUIResourceConfig()).as_blueprint()
    return blueprint
