"""add opportunity_window_score + opportunity_window_status to pain_clusters

Revision ID: 0009_add_opportunity_window_fields_to_pain_clusters
Revises: 0008_add_saturation_score_to_pain_clusters
Create Date: 2026-02-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0009_add_opportunity_window_fields_to_pain_clusters"
down_revision = "0008_add_saturation_score_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("opportunity_window_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "pain_clusters",
        sa.Column("opportunity_window_status", sa.String(), nullable=False, server_default="UNKNOWN"),
    )
    op.create_index(
        "ix_pain_clusters_opportunity_window_score",
        "pain_clusters",
        ["opportunity_window_score"],
        unique=False,
    )
    op.create_index(
        "ix_pain_clusters_opportunity_window_status",
        "pain_clusters",
        ["opportunity_window_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_opportunity_window_status", table_name="pain_clusters")
    op.drop_index("ix_pain_clusters_opportunity_window_score", table_name="pain_clusters")
    op.drop_column("pain_clusters", "opportunity_window_status")
    op.drop_column("pain_clusters", "opportunity_window_score")
