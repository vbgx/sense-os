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

    op.create_table(
        "pain_clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vertical_id", sa.Integer(), sa.ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cluster_version", sa.String(length=64), nullable=False),
        sa.Column("cluster_key", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("vertical_id", "cluster_version", "cluster_key", name="uq_pain_clusters_version_key"),
    )

    op.create_table(
        "cluster_signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("pain_clusters.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "pain_instance_id",
            sa.Integer(),
            sa.ForeignKey("pain_instances.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("cluster_id", "pain_instance_id", name="uq_cluster_signals_cluster_pain"),
    )

    op.create_table(
        "cluster_daily_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("pain_clusters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("formula_version", sa.String(length=64), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engagement", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("emerging", sa.Float(), nullable=False, server_default="0"),
        sa.Column("declining", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_volume", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_novelty", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_diversity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint(
            "cluster_id",
            "day",
            "formula_version",
            name="uq_cluster_daily_metrics_cluster_day_formula",
        ),
    )

    op.create_index("ix_signals_vertical_id", "signals", ["vertical_id"], unique=False)
    op.create_index("ix_signals_source", "signals", ["source"], unique=False)
    op.create_index("ix_signals_external_id", "signals", ["external_id"], unique=False)
    op.create_index("ix_signals_ingested_at", "signals", ["ingested_at"], unique=False)

    op.create_index("ix_pain_instances_vertical_id", "pain_instances", ["vertical_id"], unique=False)
    op.create_index("ix_pain_instances_signal_id", "pain_instances", ["signal_id"], unique=False)
    op.create_index("ix_pain_instances_algo_version", "pain_instances", ["algo_version"], unique=False)
    op.create_index("ix_pain_instances_breakdown_hash", "pain_instances", ["breakdown_hash"], unique=False)

    op.create_index(
        "ix_pain_clusters_vertical_version",
        "pain_clusters",
        ["vertical_id", "cluster_version"],
        unique=False,
    )

    op.create_index("ix_cluster_signals_cluster_id", "cluster_signals", ["cluster_id"], unique=False)
    op.create_index(
        "ix_cluster_signals_pain_instance_id",
        "cluster_signals",
        ["pain_instance_id"],
        unique=False,
    )

    op.create_index("ix_cluster_daily_metrics_day", "cluster_daily_metrics", ["day"], unique=False)
    op.create_index(
        "ix_cluster_daily_metrics_cluster_day",
        "cluster_daily_metrics",
        ["cluster_id", "day"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cluster_daily_metrics_cluster_day", table_name="cluster_daily_metrics")
    op.drop_index("ix_cluster_daily_metrics_day", table_name="cluster_daily_metrics")
    op.drop_index("ix_cluster_signals_pain_instance_id", table_name="cluster_signals")
    op.drop_index("ix_cluster_signals_cluster_id", table_name="cluster_signals")
    op.drop_index("ix_pain_clusters_vertical_version", table_name="pain_clusters")
    op.drop_index("ix_pain_instances_breakdown_hash", table_name="pain_instances")
    op.drop_index("ix_pain_instances_algo_version", table_name="pain_instances")
    op.drop_index("ix_pain_instances_signal_id", table_name="pain_instances")
    op.drop_index("ix_pain_instances_vertical_id", table_name="pain_instances")
    op.drop_index("ix_signals_ingested_at", table_name="signals")
    op.drop_index("ix_signals_external_id", table_name="signals")
    op.drop_index("ix_signals_source", table_name="signals")
    op.drop_index("ix_signals_vertical_id", table_name="signals")
    op.drop_table("cluster_daily_metrics")
    op.drop_table("cluster_signals")
    op.drop_table("pain_clusters")
    op.drop_table("pain_instances")
    op.drop_table("signals")
    op.drop_table("verticals")
