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

    # EPIC 01.04 — Monetizability Proxy Score
    monetizability_score: int = Field(0, ge=0, le=100)

    class Config:
        from_attributes = True
