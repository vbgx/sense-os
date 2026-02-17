from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ClusterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: str | int
    title: str | None = None
    cluster_summary: str | None = None
    confidence_score: int = 0


class ClusterListOut(BaseModel):
    total: int
    items: list[ClusterOut]
