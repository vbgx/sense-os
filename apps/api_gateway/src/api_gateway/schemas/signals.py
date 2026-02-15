from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SignalItem(BaseModel):
    id: int
    vertical_id: int
    source: str
    external_id: str
    content: str
    url: str | None = None
    created_at: datetime | None = None
    ingested_at: datetime | None = None

    class Config:
        from_attributes = True


class Page(BaseModel):
    limit: int
    offset: int


class SignalListOut(BaseModel):
    page: Page
    total: int
    items: list[SignalItem]
