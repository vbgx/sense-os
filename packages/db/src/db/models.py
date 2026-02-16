from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vertical(Base):
    __tablename__ = "verticals"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True, index=True)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    external_id = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    url = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    signal_quality_score = Column(Integer, nullable=True, index=True)
    language_code = Column(String(8), nullable=True, index=True)
    spam_score = Column(Integer, nullable=True, index=True)

    vertical_auto = Column(String(64), nullable=True, index=True)
    vertical_auto_confidence = Column(Integer, nullable=True, index=True)


class PainCluster(Base):
    __tablename__ = "pain_clusters"

    id = Column(Integer, primary_key=True)
    vertical_id = Column(Integer, nullable=False, index=True)

    size = Column(Integer, nullable=False, server_default="0", index=True)
    severity_score = Column(Integer, nullable=False, server_default="0", index=True)
    recurrence_score = Column(Integer, nullable=False, server_default="0", index=True)

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

    breakdown = Column(Text, nullable=True)
    breakdown_hash = Column(String(128), nullable=False, index=True)
