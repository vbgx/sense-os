from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0025_add_vertical_id_taxonomy_version_to_signals"
down_revision = "0024_add_scheduler_checkpoints_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("vertical_key", sa.String(length=255), nullable=True))
    op.add_column(
        "signals",
        sa.Column(
            "taxonomy_version",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'2026-02-17'"),
        ),
    )
    op.create_index("ix_signals_vertical_key", "signals", ["vertical_key"], unique=False)
    op.create_index("ix_signals_taxonomy_version", "signals", ["taxonomy_version"], unique=False)
    op.create_index(
        "ix_signals_vertical_key_taxonomy_created_at",
        "signals",
        ["vertical_key", "taxonomy_version", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_signals_vertical_key_taxonomy_created_at", table_name="signals")
    op.drop_index("ix_signals_taxonomy_version", table_name="signals")
    op.drop_index("ix_signals_vertical_key", table_name="signals")
    op.drop_column("signals", "taxonomy_version")
    op.drop_column("signals", "vertical_key")
