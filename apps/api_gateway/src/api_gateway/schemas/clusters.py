from __future__ import annotations

from pydantic import BaseModel


class ClusterOut(BaseModel):
    id: str
    cluster_summary: str | None = None
    confidence_score: int = 0

    class Config:
        extra = "allow"
