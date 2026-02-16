from __future__ import annotations

from pydantic import BaseModel, Field


class ClusterOut(BaseModel):
    id: str
    vertical_id: str
    title: str
    size: int

    # EPIC 01 — Pain Intelligence
    severity_score: int = Field(0, ge=0, le=100)
    recurrence_score: int = Field(0, ge=0, le=100)
    recurrence_ratio: float = Field(0.0, ge=0.0, le=1.0)
    monetizability_score: int = Field(0, ge=0, le=100)
    dominant_persona: str = Field("unknown")
    persona_confidence: float = Field(0.0, ge=0.0, le=1.0)
    persona_distribution: dict[str, float] = Field(default_factory=dict)
    contradiction_score: int = Field(0, ge=0, le=100)

    # EPIC 02 — Trend Engine Pro
    breakout_score: int = Field(0, ge=0, le=100)
    saturation_score: int = Field(0, ge=0, le=100)
    opportunity_window_score: int = Field(0, ge=0, le=100)
    opportunity_window_status: str = Field("UNKNOWN")
    half_life_days: float | None = None
    competitive_heat_score: int = Field(0, ge=0, le=100)

    # EPIC 03 — Exploitability
    exploitability_score: int = Field(0, ge=0, le=100)
    exploitability_tier: str = Field("IGNORE")
    exploitability_pain_strength: float = Field(0.0, ge=0.0, le=100.0)
    exploitability_timing_strength: float = Field(0.0, ge=0.0, le=100.0)
    exploitability_risk_penalty: float = Field(0.0, ge=0.0, le=100.0)
    exploitability_version: str = Field("")

    class Config:
        from_attributes = True
