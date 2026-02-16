"""init core tables

Revision ID: 0001_init_core_tables
Revises: 
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "verticals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vertical_id", sa.Integer(), sa.ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    op.create_table(
        "pain_instances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vertical_id", sa.Integer(), sa.ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signal_id", sa.Integer(), sa.ForeignKey("signals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("algo_version", sa.String(length=64), nullable=False),
        sa.Column("pain_score", sa.Float(), nullable=False),
        sa.Column("breakdown", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("breakdown_hash", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("algo_version", "breakdown_hash", name="uq_pain_instances_algo_breakdown"),
    )


def downgrade() -> None:
    op.drop_table("pain_instances")
    op.drop_table("signals")
    op.drop_table("verticals")
