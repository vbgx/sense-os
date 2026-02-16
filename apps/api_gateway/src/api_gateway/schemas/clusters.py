from __future__ import annotations

from pydantic import BaseModel
from typing import Any


class RepresentativeSignalOut(BaseModel):
    signal_id: str | None = None
    id: str | None = None
    user_id: str | None = None
    url: str | None = None
    title: str | None = None
    text: str | None = None

    class Config:
        extra = "allow"


class ClusterOut(BaseModel):
    id: str
    cluster_summary: str | None = None

    # 04.02
    top_signal_ids: list[str] = []
    representative_signals: list[RepresentativeSignalOut] = []

    class Config:
        extra = "allow"
