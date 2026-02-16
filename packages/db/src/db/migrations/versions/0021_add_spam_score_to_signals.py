from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0021_add_spam_score_to_signals"
down_revision = "0020_add_language_code_to_signals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("spam_score", sa.Integer(), nullable=True))
    op.create_index("ix_signals_spam_score", "signals", ["spam_score"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_signals_spam_score", table_name="signals")
    op.drop_column("signals", "spam_score")
