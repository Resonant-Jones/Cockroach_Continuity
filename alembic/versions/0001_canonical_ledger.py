"""Create the canonical continuity ledger.

Revision ID: 0001
Revises:
Create Date: 2026-08-07
"""

from __future__ import annotations

from alembic import op

from cockroach_continuity.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The initial migration deliberately uses the declared metadata as the
    # bootstrap authority so the migration and model contract cannot drift
    # before the first live schema proof. Later revisions must be explicit.
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=False)


def downgrade() -> None:
    # Reverse dependency order is supplied by SQLAlchemy metadata sorting.
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=False)
