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

    # Titan Text Embeddings V2 emits normalized 1024-dimensional vectors by
    # default. Project ID is the prefix column so vector retrieval stays scoped
    # before nearest-neighbor ranking.
    op.execute("ALTER TABLE project_events ADD COLUMN embedding VECTOR(1024)")
    op.execute("ALTER TABLE memory_assertions ADD COLUMN embedding VECTOR(1024)")
    op.execute(
        "CREATE VECTOR INDEX ix_project_events_project_embedding "
        "ON project_events (project_id, embedding)"
    )
    op.execute(
        "CREATE VECTOR INDEX ix_memory_assertions_project_embedding "
        "ON memory_assertions (project_id, embedding)"
    )


def downgrade() -> None:
    # Dropping the tables removes their vector indexes and vector columns.
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=False)
