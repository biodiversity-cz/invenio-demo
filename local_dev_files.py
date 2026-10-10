"""Local dev: serve MinIO-backed files through the app (no HTTP redirect).

With ``SITE_UI_URL`` on HTTPS and MinIO on HTTP, browsers block logo and file
previews (mixed content). Stream via Flask instead of 302 to presigned S3 URLs.

On a developer machine the patch is on. Kubernetes sets
``KUBERNETES_SERVICE_HOST``, and there the patch stays off so CESNET keeps
normal S3 redirects.

``INVENIO_LOCAL_FILES_PASSTHROUGH=1`` forces the patch on.
``INVENIO_LOCAL_FILES_PASSTHROUGH=0`` forces it off.
"""

from __future__ import annotations

import os


def _passthrough_enabled() -> bool:
    flag = os.environ.get("INVENIO_LOCAL_FILES_PASSTHROUGH")
    if flag is not None:
        return flag == "1"
    return not os.environ.get("KUBERNETES_SERVICE_HOST")


def apply_local_files_passthrough_patch() -> None:
    if not _passthrough_enabled():
        return

    from invenio_files_rest.storage import PyFSFileStorage
    from invenio_s3.storage import S3FSFileStorage

    if getattr(S3FSFileStorage, "_flowcyto_passthrough_patched", False):
        return

    def send_file_via_app(self, *args, **kwargs):
        return PyFSFileStorage.send_file(self, *args, **kwargs)

    S3FSFileStorage.send_file = send_file_via_app  # type: ignore[method-assign]
    S3FSFileStorage._flowcyto_passthrough_patched = True
