from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class Page(BaseModel):
    limit: int = Field(ge=1, le=200, default=20)
    offset: int = Field(ge=0, default=0)
    total: int = Field(ge=0, default=0)


class SparklinePoint(BaseModel):
    day: str  # ISO YYYY-MM-DD
    v: float


class TrendClusterItem(BaseModel):
    cluster_id: str
    vertical_id: int
    title: str | None = None

    score: float
    velocity: float

    source_count: int = 1
    sparkline: list[SparklinePoint] = Field(default_factory=list)


class TrendListResponse(BaseModel):
    page: Page
    items: list[TrendClusterItem]


class ScoreBreakdown(BaseModel):
    # Keep it small + stable (you can enrich later)
    volume: float | None = None
    velocity: float | None = None
    novelty: float | None = None
    diversity: float | None = None
    confidence: float | None = None


class ClusterDetail(BaseModel):
    cluster_id: str
    vertical_id: int
    day: str  # ISO

    title: str | None = None
    score: float
    velocity: float
    source_count: int = 1

    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    sparkline: list[SparklinePoint] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


class SortKey(str):
    pass


SortKind = Literal["trending", "emerging", "declining"]
