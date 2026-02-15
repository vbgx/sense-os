from datetime import datetime
from pydantic import BaseModel


class SourceLink(BaseModel):
    source: str
    external_id: str
    url: str | None = None
    created_at: datetime | None = None


class PainOut(BaseModel):
    id: int
    vertical_id: int
    signal_id: int
    algo_version: str
    pain_score: float
    breakdown: dict
    created_at: datetime | None = None
    sources: list[SourceLink]

    class Config:
        from_attributes = True


class Page(BaseModel):
    limit: int
    offset: int
    total: int


class PainListOut(BaseModel):
    page: Page
    items: list[PainOut]
