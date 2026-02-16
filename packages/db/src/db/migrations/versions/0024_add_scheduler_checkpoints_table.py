"""add scheduler_checkpoints table

Revision ID: 0024_add_scheduler_checkpoints_table
Revises: 0023_add_signal_source_external_id_unique
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0024_add_scheduler_checkpoints_table"
down_revision = "0023_add_signal_source_external_id_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scheduler_checkpoints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("vertical_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("start_day", sa.Date(), nullable=False),
        sa.Column("end_day", sa.Date(), nullable=False),
        sa.Column("last_completed_day", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="running"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("name", "vertical_id", "source", name="uq_scheduler_checkpoint"),
    )
    op.create_index("ix_scheduler_checkpoints_name", "scheduler_checkpoints", ["name"], unique=False)
    op.create_index("ix_scheduler_checkpoints_vertical_id", "scheduler_checkpoints", ["vertical_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scheduler_checkpoints_vertical_id", table_name="scheduler_checkpoints")
    op.drop_index("ix_scheduler_checkpoints_name", table_name="scheduler_checkpoints")
    op.drop_table("scheduler_checkpoints")
