from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ClusterOut(BaseModel):
    id: str
    vertical_id: str
    title: str
    size: int

    severity_score: int = Field(0, ge=0, le=100)

    recurrence_score: int = Field(0, ge=0, le=100)
    recurrence_ratio: float = Field(0.0, ge=0.0, le=1.0)

    # EPIC 01.03 — Persona Inference
    dominant_persona: str = Field("unknown")
    persona_confidence: float = Field(0.0, ge=0.0, le=1.0)
    persona_distribution: dict[str, float] = Field(default_factory=dict)

    class Config:
        from_attributes = True
