from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TimelinePointOut(BaseModel):
    date: date
    volume: int
    growth_rate: float
    velocity: float
    breakout_flag: bool


class RepresentativeSignalOut(BaseModel):
    id: str
    text: str


class ClusterDetailOut(BaseModel):
    cluster_id: str
    cluster_summary: Optional[str]

    exploitability_score: int
    exploitability_tier: str
    exploitability_score_v2: int
    exploitability_tier_v2: str
    exploitability_version_v2: str

    severity_score: int
    recurrence_score: int
    monetizability_score: int

    breakout_score: int
    opportunity_window_status: str
    competitive_heat_score: int
    contradiction_score: int

    confidence_score: int

    key_phrases: List[str]
    representative_signals: List[RepresentativeSignalOut]
    timeline: List[TimelinePointOut]

    class Config:
        extra = "ignore"

