"""Fix deposit-edit permission flags for published records.

OARepo deposit edit loads the record via ``read_draft``. For a published
record the underlying API object still has workflow ``state="draft"``, while
``status`` in the serialized payload is ``published``. Workflow rules such as
``can_new_version`` use ``IfInState("published", ...)``, so the UI wrongly
disables **New version** on the file uploader even for owners/curators.

Re-check selected actions against the published record from ``read()``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_runtime.typing import record_from_result
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources.components import PermissionsComponent, UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordItem

# Actions gated by workflow state "published" on the permission policy.
_PUBLISHED_STATE_ACTIONS = frozenset({"new_version", "lift_embargo"})


class PublishedDepositPermissionsComponent(UIResourceComponent):
    """Correct ``can_*`` flags on deposit edit for published records."""

    @override
    def before_ui_edit(
        self,
        *,
        api_record: RecordItem,
        identity: Identity,
        extra_context: dict[str, Any],
        render_kwargs: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        record_dict = api_record.to_dict()
        if not record_dict.get("is_published"):
            return

        pid = record_dict.get("id")
        if not pid:
            return

        try:
            published = self.resource.api_service.read(
                identity, pid, expand=False
            )
        except Exception:
            return

        published_record = record_from_result(published)
        perm_helper = PermissionsComponent(self.resource)
        actions = current_oarepo_ui.record_actions
        published_actions = {
            name: name for name in actions if name in _PUBLISHED_STATE_ACTIONS
        }
        if not published_actions:
            return

        flags = perm_helper.get_record_permissions(
            published_actions,
            self.resource.api_service,
            identity,
            published_record,
        )

        permissions = render_kwargs.get("permissions") or extra_context.get(
            "permissions"
        )
        if not isinstance(permissions, dict):
            return

        permissions.update(flags)
        extra_context["permissions"] = permissions
        render_kwargs["permissions"] = permissions
