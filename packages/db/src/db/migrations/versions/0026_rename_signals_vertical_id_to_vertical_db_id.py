from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0026_rename_signals_vertical_id_to_vertical_db_id"
down_revision = "0025_add_vertical_id_taxonomy_version_to_signals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_signals_vertical_key_taxonomy_created_at", table_name="signals")
    op.drop_index("ix_signals_vertical_key", table_name="signals")
    op.drop_column("signals", "vertical_key")

    op.drop_index("ix_signals_vertical_id", table_name="signals")
    op.alter_column("signals", "vertical_id", new_column_name="vertical_db_id")
    op.create_index("ix_signals_vertical_db_id", "signals", ["vertical_db_id"], unique=False)

    op.add_column("signals", sa.Column("vertical_id", sa.String(length=255), nullable=True))
    op.create_index("ix_signals_vertical_id", "signals", ["vertical_id"], unique=False)
    op.create_index(
        "ix_signals_vertical_id_taxonomy_created_at",
        "signals",
        ["vertical_id", "taxonomy_version", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_signals_vertical_id_taxonomy_created_at", table_name="signals")
    op.drop_index("ix_signals_vertical_id", table_name="signals")
    op.drop_column("signals", "vertical_id")

    op.drop_index("ix_signals_vertical_db_id", table_name="signals")
    op.alter_column("signals", "vertical_db_id", new_column_name="vertical_id")
    op.create_index("ix_signals_vertical_id", "signals", ["vertical_id"], unique=False)

    op.add_column("signals", sa.Column("vertical_key", sa.String(length=255), nullable=True))
    op.create_index("ix_signals_vertical_key", "signals", ["vertical_key"], unique=False)
    op.create_index(
        "ix_signals_vertical_key_taxonomy_created_at",
        "signals",
        ["vertical_key", "taxonomy_version", "created_at"],
        unique=False,
    )
