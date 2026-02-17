"""add breakout_score to pain_clusters

Revision ID: 0007_add_breakout_score_to_pain_clusters
Revises: 0006_add_contradiction_score_to_pain_clusters
Create Date: 2026-02-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0007_add_breakout_score_to_pain_clusters"
down_revision = "0006_add_contradiction_score_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("breakout_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_pain_clusters_breakout_score",
        "pain_clusters",
        ["breakout_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_breakout_score", table_name="pain_clusters")
    op.drop_column("pain_clusters", "breakout_score")
