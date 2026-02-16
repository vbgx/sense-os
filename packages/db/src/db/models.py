from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

Base = declarative_base()


class Vertical(Base):
    __tablename__ = "verticals"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_signals_source_external_id"),
    )

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, nullable=False, index=True)
    source = Column(String(64), nullable=False, index=True)
    external_id = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    url = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    ingested_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), index=True)

    signal_quality_score = Column(Integer, nullable=True, index=True)
    language_code = Column(String(8), nullable=True, index=True)
    spam_score = Column(Integer, nullable=True, index=True)

    vertical_auto = Column(String(64), nullable=True, index=True)
    vertical_auto_confidence = Column(Integer, nullable=True, index=True)


class PainCluster(Base):
    __tablename__ = "pain_clusters"
    __table_args__ = (
        UniqueConstraint("vertical_id", "cluster_version", "cluster_key", name="uq_pain_clusters_version_key"),
    )

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, nullable=False, index=True)
    cluster_version = Column(String(64), nullable=False, index=True)
    cluster_key = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False, server_default="0", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    severity_score = Column(Integer, nullable=False, server_default="0", index=True)
    recurrence_score = Column(Integer, nullable=False, server_default="0", index=True)
    recurrence_ratio = Column(Float, nullable=False, server_default="0")

    dominant_persona = Column(String(), nullable=False, server_default="unknown", index=True)
    persona_confidence = Column(Float, nullable=False, server_default="0")
    persona_distribution_json = Column(Text, nullable=False, server_default="{}")

    monetizability_score = Column(Integer, nullable=False, server_default="0", index=True)
    contradiction_score = Column(Integer, nullable=False, server_default="0", index=True)
    breakout_score = Column(Integer, nullable=False, server_default="0", index=True)
    saturation_score = Column(Integer, nullable=False, server_default="0", index=True)

    opportunity_window_score = Column(Integer, nullable=False, server_default="0", index=True)
    opportunity_window_status = Column(String(), nullable=False, server_default="UNKNOWN", index=True)
    half_life_days = Column(Float, nullable=True, index=True)
    competitive_heat_score = Column(Integer, nullable=False, server_default="0", index=True)

    exploitability_score = Column(Integer, nullable=False, server_default="0", index=True)
    exploitability_pain_strength = Column(Float, nullable=False, server_default="0")
    exploitability_timing_strength = Column(Float, nullable=False, server_default="0")
    exploitability_risk_penalty = Column(Float, nullable=False, server_default="0")
    exploitability_version = Column(String(), nullable=False, server_default="", index=True)
    exploitability_tier = Column(String(), nullable=False, server_default="IGNORE", index=True)

    cluster_summary = Column(Text, nullable=True)
    top_signal_ids_json = Column(Text, nullable=False, server_default="[]")
    key_phrases_json = Column(Text, nullable=False, server_default="[]")
    confidence_score = Column(Integer, nullable=False, server_default="0", index=True)


class PainInstance(Base):
    __tablename__ = "pain_instances"
    __table_args__ = (
        UniqueConstraint("algo_version", "breakdown_hash", name="uq_pain_instances_algo_breakdown"),
    )

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, nullable=False, index=True)
    signal_id = Column(Integer, nullable=False, index=True)

    algo_version = Column(String(64), nullable=False, index=True)
    pain_score = Column(Float, nullable=False, server_default="0")

    breakdown = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    breakdown_hash = Column(String(32), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ClusterSignal(Base):
    __tablename__ = "cluster_signals"
    __table_args__ = (
        UniqueConstraint("cluster_id", "pain_instance_id", name="uq_cluster_signals_cluster_pain"),
    )

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, nullable=False, index=True)
    pain_instance_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ClusterDailyMetric(Base):
    __tablename__ = "cluster_daily_metrics"
    __table_args__ = (
        UniqueConstraint(
            "cluster_id",
            "day",
            "formula_version",
            name="uq_cluster_daily_metrics_cluster_day_formula",
        ),
    )

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, nullable=False, index=True)
    day = Column(Date, nullable=False, index=True)
    formula_version = Column(String(64), nullable=False, index=True)

    frequency = Column(Integer, nullable=False, server_default="0")
    engagement = Column(Integer, nullable=False, server_default="0")
    avg_score = Column(Float, nullable=False, server_default="0")
    source_count = Column(Integer, nullable=False, server_default="0")

    velocity = Column(Float, nullable=False, server_default="0")
    emerging = Column(Float, nullable=False, server_default="0")
    declining = Column(Float, nullable=False, server_default="0")

    score = Column(Float, nullable=False, server_default="0")
    score_volume = Column(Float, nullable=False, server_default="0")
    score_velocity = Column(Float, nullable=False, server_default="0")
    score_novelty = Column(Float, nullable=False, server_default="0")
    score_diversity = Column(Float, nullable=False, server_default="0")
    score_confidence = Column(Float, nullable=False, server_default="0")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ClusterDailyHistory(Base):
    __tablename__ = "cluster_daily_history"

    cluster_id = Column(String(), primary_key=True)
    day = Column(Date, primary_key=True)
    volume = Column(Integer, nullable=False, server_default="0")
    growth_rate = Column(Float, nullable=False, server_default="0")
    velocity = Column(Float, nullable=False, server_default="0")
    breakout_flag = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))


class SchedulerCheckpoint(Base):
    __tablename__ = "scheduler_checkpoints"
    __table_args__ = (
        UniqueConstraint("name", "vertical_id", "source", name="uq_scheduler_checkpoint"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, index=True)
    vertical_id = Column(Integer, nullable=False, index=True)
    source = Column(String(64), nullable=False)
    start_day = Column(Date, nullable=False)
    end_day = Column(Date, nullable=False)
    last_completed_day = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, server_default="running")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
