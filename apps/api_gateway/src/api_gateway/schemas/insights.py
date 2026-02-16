from __future__ import annotations

from pydantic import BaseModel


class TopPainOut(BaseModel):
    cluster_id: str
    cluster_summary: str | None
    exploitability_score: int
    exploitability_tier: str
    severity_score: int
    breakout_score: int
    opportunity_window_status: str
    confidence_score: int
    dominant_persona: str

    class Config:
        extra = "ignore"
