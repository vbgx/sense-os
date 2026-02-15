from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ClusterItem(BaseModel):
    id: int
    vertical_id: int
    cluster_version: str
    cluster_key: str
    title: str
    size: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class Page(BaseModel):
    limit: int
    offset: int


class ClusterListOut(BaseModel):
    page: Page
    total: int
    items: list[ClusterItem]
