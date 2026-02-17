"""add half_life_days to pain_clusters

Revision ID: 0010_add_half_life_days_to_pain_clusters
Revises: 0009_add_opportunity_window_fields_to_pain_clusters
Create Date: 2026-02-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0010_add_half_life_days_to_pain_clusters"
down_revision = "0009_add_opportunity_window_fields_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("half_life_days", sa.Float(), nullable=True),
    )
    op.create_index(
        "ix_pain_clusters_half_life_days",
        "pain_clusters",
        ["half_life_days"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_half_life_days", table_name="pain_clusters")
    op.drop_column("pain_clusters", "half_life_days")
