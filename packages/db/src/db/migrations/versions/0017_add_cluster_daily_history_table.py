"""add cluster_daily_history table

Revision ID: 0017_add_cluster_daily_history
Revises: 0016_add_key_phrases_json
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0017_add_cluster_daily_history"
down_revision = "0016_add_key_phrases_json"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cluster_daily_history",
        sa.Column("cluster_id", sa.String(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("growth_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("breakout_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("cluster_id", "day", name="pk_cluster_daily_history"),
    )
    op.create_index(
        "ix_cluster_daily_history_cluster_day",
        "cluster_daily_history",
        ["cluster_id", "day"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cluster_daily_history_cluster_day", table_name="cluster_daily_history")
    op.drop_table("cluster_daily_history")
