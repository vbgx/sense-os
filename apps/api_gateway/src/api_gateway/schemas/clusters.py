from __future__ import annotations

from pydantic import BaseModel, Field


class ClusterOut(BaseModel):
    id: str
    vertical_id: str
    title: str
    size: int

    severity_score: int = Field(0, ge=0, le=100)

    recurrence_score: int = Field(0, ge=0, le=100)
    recurrence_ratio: float = Field(0.0, ge=0.0, le=1.0)

    dominant_persona: str = Field("unknown")
    persona_confidence: float = Field(0.0, ge=0.0, le=1.0)
    persona_distribution: dict[str, float] = Field(default_factory=dict)

    monetizability_score: int = Field(0, ge=0, le=100)
    contradiction_score: int = Field(0, ge=0, le=100)

    breakout_score: int = Field(0, ge=0, le=100)
    saturation_score: int = Field(0, ge=0, le=100)

    # EPIC 02.03 — Opportunity Window
    opportunity_window_score: int = Field(0, ge=0, le=100)
    opportunity_window_status: str = Field("UNKNOWN")

    class Config:
        from_attributes = True
