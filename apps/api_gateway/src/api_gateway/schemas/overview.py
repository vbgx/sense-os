# api_gateway/src/api_gateway/schemas/overview.py
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OverviewStatus(str, Enum):
    hot = "hot"
    emerging = "emerging"
    stable = "stable"
    saturated = "saturated"
    declining = "declining"


class OverviewKpiOut(BaseModel):
    key: str = Field(..., description="Stable machine key, e.g. total_active_verticals")
    label: str = Field(..., description="UI label")
    value: float = Field(..., description="Numeric KPI value")
    delta_7d: Optional[float] = Field(default=None, description="7-day delta, if available")
    sparkline: Optional[List[float]] = Field(default=None, description="Optional micro sparkline values")


class OverviewBreakoutOut(BaseModel):
    rank: int = Field(..., ge=1)
    vertical_id: str = Field(..., description="Vertical identifier (string id)")
    vertical_label: str = Field(..., description="Display label")
    score: float = Field(..., description="Opportunity score (0-100 or normalized)")
    momentum_7d: float = Field(..., description="7-day momentum")
    confidence: float = Field(..., ge=0.0, le=1.0)
    tier: Optional[str] = Field(default=None, description="core/edge/test/etc.")
    status: OverviewStatus = Field(...)


class OverviewHeatmapCellOut(BaseModel):
    industry: str
    function: str
    value: float = Field(..., description="Opportunity density / intensity for this cell")
    top_vertical_id: Optional[str] = None
    top_vertical_label: Optional[str] = None
    avg_score: Optional[float] = None
    momentum_7d: Optional[float] = None


class OverviewOut(BaseModel):
    updated_at: str = Field(..., description="ISO datetime")
    kpis: List[OverviewKpiOut]
    breakouts: List[OverviewBreakoutOut] = Field(default_factory=list, description="Top 10 breakouts")
    heatmap: List[OverviewHeatmapCellOut] = Field(default_factory=list, description="Industry x Function cells")
