from __future__ import annotations

from pydantic import BaseModel


class ClusterOut(BaseModel):
    id: str
    cluster_summary: str | None = None

    class Config:
        extra = "allow"
