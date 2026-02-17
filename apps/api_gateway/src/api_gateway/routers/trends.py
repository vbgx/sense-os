from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api_gateway.schemas.trends import (
    TrendListResponse,
    ClusterDetail,
    InsightTopPainsResponse,
)
from api_gateway.dependencies import get_trends_use_case
from application.use_cases.trends import TrendsUseCase, build_query, build_top_pains_query

router = APIRouter(tags=["trends"])


@router.get("/trending", response_model=TrendListResponse)
def get_trending(
    use_case: TrendsUseCase = Depends(get_trends_use_case),
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None, description="ISO YYYY-MM-DD; default is yesterday"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sparkline_days: int = Query(14, ge=2, le=90),
    min_exploitability: int | None = Query(default=None, ge=0, le=100),
    max_exploitability: int | None = Query(default=None, ge=0, le=100),
):
    q = build_query(
        vertical_id=vertical_id,
        day=day,
        limit=limit,
        offset=offset,
        sparkline_days=sparkline_days,
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
    )
    return use_case.list_trending(q)


@router.get("/emerging", response_model=TrendListResponse)
def get_emerging(
    use_case: TrendsUseCase = Depends(get_trends_use_case),
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sparkline_days: int = Query(14, ge=2, le=90),
    min_exploitability: int | None = Query(default=None, ge=0, le=100),
    max_exploitability: int | None = Query(default=None, ge=0, le=100),
):
    q = build_query(
        vertical_id=vertical_id,
        day=day,
        limit=limit,
        offset=offset,
        sparkline_days=sparkline_days,
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
    )
    return use_case.list_emerging(q)


@router.get("/declining", response_model=TrendListResponse)
def get_declining(
    use_case: TrendsUseCase = Depends(get_trends_use_case),
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sparkline_days: int = Query(14, ge=2, le=90),
    min_exploitability: int | None = Query(default=None, ge=0, le=100),
    max_exploitability: int | None = Query(default=None, ge=0, le=100),
):
    q = build_query(
        vertical_id=vertical_id,
        day=day,
        limit=limit,
        offset=offset,
        sparkline_days=sparkline_days,
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
    )
    return use_case.list_declining(q)


@router.get("/clusters/{cluster_id}", response_model=ClusterDetail)
def get_cluster_detail(
    cluster_id: str,
    use_case: TrendsUseCase = Depends(get_trends_use_case),
    vertical_id: int = Query(..., ge=1),
    day: str | None = Query(None),
    sparkline_days: int = Query(30, ge=2, le=180),
):
    return use_case.get_cluster_detail(
        vertical_id=int(vertical_id),
        cluster_id=str(cluster_id),
        day=day or "",
        sparkline_days=int(sparkline_days),
    )


@router.get("/insights/top_pains", response_model=InsightTopPainsResponse, tags=["insights"])
def insights_top_pains(
    use_case: TrendsUseCase = Depends(get_trends_use_case),
    vertical_id: int = Query(..., ge=1),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    min_exploitability: int | None = Query(default=None, ge=0, le=100),
    max_exploitability: int | None = Query(default=None, ge=0, le=100),
):
    q = build_top_pains_query(
        vertical_id=vertical_id,
        limit=limit,
        offset=offset,
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
    )
    return use_case.list_top_pains(q)
