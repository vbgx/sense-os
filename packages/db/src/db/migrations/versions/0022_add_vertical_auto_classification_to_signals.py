from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0022_add_vertical_auto_classification_to_signals"
down_revision = "0021_add_spam_score_to_signals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("vertical_auto", sa.String(length=64), nullable=True))
    op.add_column("signals", sa.Column("vertical_auto_confidence", sa.Integer(), nullable=True))
    op.create_index("ix_signals_vertical_auto", "signals", ["vertical_auto"], unique=False)
    op.create_index("ix_signals_vertical_auto_confidence", "signals", ["vertical_auto_confidence"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_signals_vertical_auto_confidence", table_name="signals")
    op.drop_index("ix_signals_vertical_auto", table_name="signals")
    op.drop_column("signals", "vertical_auto_confidence")
    op.drop_column("signals", "vertical_auto")
