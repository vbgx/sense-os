from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0020_add_language_code_to_signals"
down_revision = "0019_add_signal_quality_and_created_at_to_signals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("language_code", sa.String(length=8), nullable=True))
    op.create_index("ix_signals_language_code", "signals", ["language_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_signals_language_code", table_name="signals")
    op.drop_column("signals", "language_code")
