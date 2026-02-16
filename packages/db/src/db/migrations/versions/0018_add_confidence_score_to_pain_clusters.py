"""add confidence_score to pain_clusters

Revision ID: 0018_add_confidence_score
Revises: 0017_add_cluster_daily_history
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0018_add_confidence_score"
down_revision = "0017_add_cluster_daily_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_pain_clusters_confidence_score",
        "pain_clusters",
        ["confidence_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_confidence_score", table_name="pain_clusters")
    op.drop_column("pain_clusters", "confidence_score")
