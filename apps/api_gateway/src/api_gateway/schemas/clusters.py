from __future__ import annotations

from pydantic import BaseModel, Field


class ClusterOut(BaseModel):
    id: str
    vertical_id: str
    title: str
    size: int

    # EPIC 01.01 — Pain Severity Index
    severity_score: int = Field(0, ge=0, le=100)

    # EPIC 01.02 — Recurrence Detection
    recurrence_score: int = Field(0, ge=0, le=100)
    recurrence_ratio: float = Field(0.0, ge=0.0, le=1.0)

    class Config:
        from_attributes = True
