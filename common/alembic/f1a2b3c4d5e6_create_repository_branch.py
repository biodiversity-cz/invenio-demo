#
# Create the application Alembic branch for flowcyto schema changes.
#

"""Create repository branch."""

from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "f1a2b3c4d5e6"
down_revision = None
branch_labels = ("repository",)
depends_on = None


def upgrade() -> None:
    """Upgrade database."""


def downgrade() -> None:
    """Downgrade database."""
