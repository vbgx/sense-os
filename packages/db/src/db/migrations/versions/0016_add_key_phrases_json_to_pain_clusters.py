"""add key_phrases_json to pain_clusters

Revision ID: 0016_add_key_phrases_json
Revises: 0015_add_top_signal_ids_json
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0016_add_key_phrases_json"
down_revision = "0015_add_top_signal_ids_json"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pain_clusters",
        sa.Column("key_phrases_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.create_index(
        "ix_pain_clusters_key_phrases_json",
        "pain_clusters",
        ["key_phrases_json"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pain_clusters_key_phrases_json", table_name="pain_clusters")
    op.drop_column("pain_clusters", "key_phrases_json")
