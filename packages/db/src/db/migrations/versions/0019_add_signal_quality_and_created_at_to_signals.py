from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0019_add_signal_quality_and_created_at_to_signals"
down_revision = "0018_add_confidence_score_to_pain_clusters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("signals", sa.Column("signal_quality_score", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("signals", "signal_quality_score")
    op.drop_column("signals", "created_at")
