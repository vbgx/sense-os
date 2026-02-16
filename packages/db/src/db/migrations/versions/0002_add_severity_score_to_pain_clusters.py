"""add severity_score to pain_clusters

Revision ID: 0002_add_severity_score_to_pain_clusters
Revises: 0001_init_core_tables
Create Date: 2026-02-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_severity_score_to_pain_clusters"
down_revision = "0001_init_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("severity_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_pain_clusters_severity_score",
        "pain_clusters",
        ["severity_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_severity_score", table_name="pain_clusters")
    op.drop_column("pain_clusters", "severity_score")
