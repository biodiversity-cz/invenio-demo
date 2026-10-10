#
# Add parent.workflow column required by oarepo-workflows workflows_preset.
# On a fresh install, ``invenio db create`` already creates this column from
# the SQLAlchemy model; this revision is for upgrades of existing databases.
#

"""Add workflow column to cytometry_parent_metadata."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a7c9e2f1b4d8"
down_revision = "f1a2b3c4d5e6"
branch_labels = ()
depends_on = None


def upgrade() -> None:
    """Upgrade database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "cytometry_parent_metadata" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("cytometry_parent_metadata")}
    if "workflow" not in columns:
        op.add_column(
            "cytometry_parent_metadata",
            sa.Column("workflow", sa.String(), nullable=True),
        )


def downgrade() -> None:
    """Downgrade database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "cytometry_parent_metadata" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("cytometry_parent_metadata")}
    if "workflow" in columns:
        op.drop_column("cytometry_parent_metadata", "workflow")
