from __future__ import annotations

from fastapi import APIRouter, Query
from typing import List, Optional

from api_gateway.schemas.insights import TopPainOut
from api_gateway.schemas.cluster_detail import ClusterDetailOut
from api_gateway.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/top_pains", response_model=List[TopPainOut])
def get_top_pains(
    vertical_id: Optional[str] = None,
    tier: Optional[str] = None,
    emerging_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    service = InsightsService()
    return service.get_top_pains(
        vertical_id=vertical_id,
        tier=tier,
        emerging_only=emerging_only,
        limit=limit,
        offset=offset,
    )


@router.get("/emerging_opportunities", response_model=List[TopPainOut])
def get_emerging_opportunities(
    vertical_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    service = InsightsService()
    return service.get_emerging_opportunities(
        vertical_id=vertical_id,
        limit=limit,
        offset=offset,
    )


@router.get("/declining_risks", response_model=List[TopPainOut])
def get_declining_risks(
    vertical_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    service = InsightsService()
    return service.get_declining_risks(
        vertical_id=vertical_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{cluster_id}", response_model=ClusterDetailOut)
def get_cluster_detail(cluster_id: str):
    service = InsightsService()
    return service.get_cluster_detail(cluster_id=cluster_id)
