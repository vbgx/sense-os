"""add unique constraint on signals source/external_id

Revision ID: 0023_add_signal_source_external_id_unique
Revises: 0022_add_vertical_auto_classification_to_signals
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0023_add_signal_source_external_id_unique"
down_revision = "0022_add_vertical_auto_classification_to_signals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_signals_source_external_id",
        "signals",
        ["source", "external_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_signals_source_external_id", "signals", type_="unique")
