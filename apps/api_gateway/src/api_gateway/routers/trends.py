from __future__ import annotations

from fastapi import APIRouter, Query

from api_gateway.schemas.trends import (
    TrendListResponse,
    ClusterDetail,
)
from api_gateway.services.trends_service import TrendsService, build_query

router = APIRouter(tags=["trends"])

_service = TrendsService()


@router.get("/trending", response_model=TrendListResponse)
def get_trending(
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None, description="ISO YYYY-MM-DD; default is yesterday"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sparkline_days: int = Query(14, ge=2, le=90),
):
    q = build_query(vertical_id=vertical_id, day=day, limit=limit, offset=offset, sparkline_days=sparkline_days)
    return _service.list_trending(q)


@router.get("/emerging", response_model=TrendListResponse)
def get_emerging(
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sparkline_days: int = Query(14, ge=2, le=90),
):
    q = build_query(vertical_id=vertical_id, day=day, limit=limit, offset=offset, sparkline_days=sparkline_days)
    return _service.list_emerging(q)


@router.get("/declining", response_model=TrendListResponse)
def get_declining(
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sparkline_days: int = Query(14, ge=2, le=90),
):
    q = build_query(vertical_id=vertical_id, day=day, limit=limit, offset=offset, sparkline_days=sparkline_days)
    return _service.list_declining(q)


@router.get("/clusters/{cluster_id}", response_model=ClusterDetail)
def get_cluster_detail(
    cluster_id: str,
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None),
    sparkline_days: int = Query(30, ge=2, le=180),
):
    # day default handled in service
    return _service.get_cluster_detail(
        vertical_id=int(vertical_id),
        cluster_id=str(cluster_id),
        day=day or "",
        sparkline_days=int(sparkline_days),
    )
