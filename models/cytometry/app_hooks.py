"""Invenio app hooks for the cytometry model."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def finalize_app(app: Flask) -> None:
    """Register runtime service components after the app context exists.

    During ``./run.sh install`` the app is probed before ``invenio.cfg``
    registers the model. Skip quietly in that case; the component is also
    attached by ``AddServiceComponent`` once the model is built.
    """
    with app.app_context():
        from oarepo_runtime.proxies import current_runtime

        from .service_components import MeasurerNameCompatComponent

        model = current_runtime.models.get("cytometry")
        if model is None:
            return
        cfg = getattr(model, "service_config", None)
        if cfg is None or not hasattr(cfg, "components"):
            return
        components = tuple(cfg.components)
        if MeasurerNameCompatComponent not in components:
            cfg.components = components + (MeasurerNameCompatComponent,)
