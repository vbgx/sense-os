"""add cluster_summary to pain_clusters

Revision ID: 0014_add_cluster_summary
Revises: 0013_add_exploitability_tier_to_pain_clusters
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

# NOTE: keep consistent with your existing migration chain
revision = "0014_add_cluster_summary"
down_revision = "0013_add_exploitability_tier_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pain_clusters", sa.Column("cluster_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("pain_clusters", "cluster_summary")
