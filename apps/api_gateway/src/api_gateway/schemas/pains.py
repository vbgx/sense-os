from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SignalOut(BaseModel):
    id: int | None = None
    source: str | None = None
    url: str | None = None
    title: str | None = None
    ingested_at: datetime | None = None


class PainItem(BaseModel):
    id: int
    vertical_id: int
    algo_version: str
    pain_score: float
    breakdown: dict
    created_at: datetime | None = None
    signal: SignalOut | None = None

    class Config:
        from_attributes = True


class Page(BaseModel):
    limit: int
    offset: int


class PainListOut(BaseModel):
    page: Page
    total: int
    items: list[PainItem]


class PainDetailOut(PainItem):
    pass
