from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text, Boolean, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Vertical(Base):
    __tablename__ = "verticals"

    id = Column(String, primary_key=True)
    slug = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"

    id = Column(String, primary_key=True)
    vertical_id = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    upvotes = Column(Integer, nullable=False, server_default="0")
    comments = Column(Integer, nullable=False, server_default="0")
    replies = Column(Integer, nullable=False, server_default="0")
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class PainInstance(Base):
    __tablename__ = "pain_instances"

    id = Column(String, primary_key=True)
    vertical_id = Column(String, nullable=False, index=True)
    signal_id = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    sentiment_compound = Column(Float, nullable=True)
    pain_score = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class PainCluster(Base):
    __tablename__ = "pain_clusters"

    id = Column(String, primary_key=True)
    vertical_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    size = Column(Integer, nullable=False, server_default="0")

    # EPIC 01
    severity_score = Column(Integer, nullable=False, server_default="0", index=True)
    recurrence_score = Column(Integer, nullable=False, server_default="0", index=True)
    recurrence_ratio = Column(Float, nullable=False, server_default="0")
    dominant_persona = Column(String, nullable=False, server_default="unknown", index=True)
    persona_confidence = Column(Float, nullable=False, server_default="0")
    persona_distribution_json = Column(Text, nullable=False, server_default="{}")
    monetizability_score = Column(Integer, nullable=False, server_default="0", index=True)
    contradiction_score = Column(Integer, nullable=False, server_default="0", index=True)

    # EPIC 02
    breakout_score = Column(Integer, nullable=False, server_default="0", index=True)
    saturation_score = Column(Integer, nullable=False, server_default="0", index=True)
    opportunity_window_score = Column(Integer, nullable=False, server_default="0", index=True)
    opportunity_window_status = Column(String, nullable=False, server_default="UNKNOWN", index=True)
    half_life_days = Column(Float, nullable=True, index=True)
    competitive_heat_score = Column(Integer, nullable=False, server_default="0", index=True)

    # EPIC 03
    exploitability_score = Column(Integer, nullable=False, server_default="0", index=True)
    exploitability_pain_strength = Column(Float, nullable=False, server_default="0")
    exploitability_timing_strength = Column(Float, nullable=False, server_default="0")
    exploitability_risk_penalty = Column(Float, nullable=False, server_default="0")
    exploitability_version = Column(String, nullable=False, server_default="", index=True)
    exploitability_tier = Column(String, nullable=False, server_default="IGNORE", index=True)

    # EPIC 04
    cluster_summary = Column(Text, nullable=True)
    top_signal_ids_json = Column(Text, nullable=False, server_default="[]")
    key_phrases_json = Column(Text, nullable=False, server_default="[]")

    created_at = Column(DateTime, nullable=False, server_default=func.now())


class ClusterDailyHistory(Base):
    __tablename__ = "cluster_daily_history"

    cluster_id = Column(String, primary_key=True)
    day = Column(Date, primary_key=True)

    volume = Column(Integer, nullable=False, server_default="0")
    growth_rate = Column(Float, nullable=False, server_default="0")
    velocity = Column(Float, nullable=False, server_default="0")
    breakout_flag = Column(Boolean, nullable=False, server_default="false")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
