"""add top_signal_ids_json to pain_clusters

Revision ID: 0015_add_top_signal_ids_json
Revises: 0014_add_cluster_summary
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0015_add_top_signal_ids_json"
down_revision = "0014_add_cluster_summary"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("top_signal_ids_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.create_index(
        "ix_pain_clusters_top_signal_ids_json",
        "pain_clusters",
        ["top_signal_ids_json"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_top_signal_ids_json", table_name="pain_clusters")
    op.drop_column("pain_clusters", "top_signal_ids_json")
