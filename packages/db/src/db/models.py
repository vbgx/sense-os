from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    JSON,
    func,
)

Base = declarative_base()


class Vertical(Base):
    __tablename__ = "verticals"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_signals_source_external_id"),)

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(64), nullable=False)
    external_id = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PainInstance(Base):
    __tablename__ = "pain_instances"
    __table_args__ = (
        UniqueConstraint("algo_version", "breakdown_hash", name="uq_pain_instances_algo_breakdown"),
    )

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False)
    algo_version = Column(String(64), nullable=False)
    pain_score = Column(Float, nullable=False)
    breakdown = Column(JSON, nullable=False, default=dict)
    breakdown_hash = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PainCluster(Base):
    __tablename__ = "pain_clusters"
    __table_args__ = (
        UniqueConstraint("vertical_id", "cluster_version", "cluster_key", name="uq_pain_clusters_version_key"),
    )

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False)
    cluster_version = Column(String(64), nullable=False)
    cluster_key = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ClusterSignal(Base):
    __tablename__ = "cluster_signals"
    __table_args__ = (
        UniqueConstraint("cluster_id", "pain_instance_id", name="uq_cluster_signals_cluster_pain"),
    )

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("pain_clusters.id", ondelete="CASCADE"), nullable=False)
    pain_instance_id = Column(Integer, ForeignKey("pain_instances.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


from datetime import date as _date
from sqlalchemy import Date as _Date


class ClusterDailyMetric(Base):
    __tablename__ = "cluster_daily_metrics"
    __table_args__ = (
        UniqueConstraint("cluster_id", "day", "formula_version", name="uq_cluster_daily_metrics_cluster_day_formula"),
    )

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("pain_clusters.id", ondelete="CASCADE"), nullable=False)

    day = Column(_Date(), nullable=False)
    formula_version = Column(String(64), nullable=False)

    frequency = Column(Integer, nullable=False, default=0)
    engagement = Column(Integer, nullable=False, default=0)
    avg_score = Column(Float, nullable=False, default=0.0)
    source_count = Column(Integer, nullable=False, default=0)

    # trend signals
    velocity = Column(Float, nullable=False, default=0.0)
    emerging = Column(Float, nullable=False, default=0.0)
    declining = Column(Float, nullable=False, default=0.0)

    # API expected fields
    score = Column(Float, nullable=False, default=0.0)
    score_volume = Column(Float, nullable=False, default=0.0)
    score_velocity = Column(Float, nullable=False, default=0.0)
    score_novelty = Column(Float, nullable=False, default=0.0)
    score_diversity = Column(Float, nullable=False, default=0.0)
    score_confidence = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
