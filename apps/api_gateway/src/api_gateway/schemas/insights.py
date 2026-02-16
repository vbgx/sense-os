from __future__ import annotations

from pydantic import BaseModel
from typing import Optional
from api_gateway.schemas.build_signal import BuildSignalOut


class TopPainOut(BaseModel):
    cluster_id: str
    cluster_summary: Optional[str]
    exploitability_score: int
    exploitability_tier: str
    severity_score: int
    breakout_score: int
    opportunity_window_status: str
    confidence_score: int
    dominant_persona: str
    build_signal: BuildSignalOut

    class Config:
        extra = "ignore"
