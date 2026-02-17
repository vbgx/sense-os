"""add recurrence_score + recurrence_ratio to pain_clusters

Revision ID: 0003_add_recurrence_score_to_pain_clusters
Revises: 0002_add_severity_score_to_pain_clusters
Create Date: 2026-02-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_add_recurrence_score_to_pain_clusters"
down_revision = "0002_add_severity_score_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("recurrence_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "pain_clusters",
        sa.Column("recurrence_ratio", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_pain_clusters_recurrence_score",
        "pain_clusters",
        ["recurrence_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_recurrence_score", table_name="pain_clusters")
    op.drop_column("pain_clusters", "recurrence_ratio")
    op.drop_column("pain_clusters", "recurrence_score")
