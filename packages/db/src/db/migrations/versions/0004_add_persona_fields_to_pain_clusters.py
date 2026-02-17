"""add dominant_persona + persona_distribution + persona_confidence to pain_clusters

Revision ID: 0004_add_persona_fields_to_pain_clusters
Revises: 0003_add_recurrence_score_to_pain_clusters
Create Date: 2026-02-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0004_add_persona_fields_to_pain_clusters"
down_revision = "0003_add_recurrence_score_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("dominant_persona", sa.String(), nullable=False, server_default="unknown"),
    )
    op.add_column(
        "pain_clusters",
        sa.Column("persona_confidence", sa.Float(), nullable=False, server_default="0"),
    )
    # JSON stored as TEXT for portability (SQLite/Postgres); API exposes as dict.
    op.add_column(
        "pain_clusters",
        sa.Column("persona_distribution_json", sa.Text(), nullable=False, server_default="{}"),
    )
    op.create_index(
        "ix_pain_clusters_dominant_persona",
        "pain_clusters",
        ["dominant_persona"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_dominant_persona", table_name="pain_clusters")
    op.drop_column("pain_clusters", "persona_distribution_json")
    op.drop_column("pain_clusters", "persona_confidence")
    op.drop_column("pain_clusters", "dominant_persona")
