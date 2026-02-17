from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime


class MetaStatusOut(BaseModel):
    last_run_at: datetime | None
    scoring_version: str
    total_signals_7d: int
    total_clusters: int

    class Config:
        extra = "ignore"
