from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, List, Optional

from api_gateway.schemas.insights import TopPainOut
from api_gateway.schemas.cluster_detail import ClusterDetailOut
from api_gateway.schemas.export_payload import VentureOSExportPayloadV1Schema
from api_gateway.dependencies import get_insights_use_case
from application.ports import NotFoundError
from application.use_cases.insights import InsightsUseCase

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/top_pains", response_model=List[TopPainOut])
def get_top_pains(
    use_case: InsightsUseCase = Depends(get_insights_use_case),
    vertical_id: Annotated[str | None, Query()] = None,
    tier: Annotated[str | None, Query()] = None,
    emerging_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return use_case.get_top_pains(
        vertical_id=vertical_id,
        tier=tier,
        emerging_only=emerging_only,
        limit=limit,
        offset=offset,
    )


@router.get("/emerging_opportunities", response_model=List[TopPainOut])
def get_emerging_opportunities(
    use_case: InsightsUseCase = Depends(get_insights_use_case),
    vertical_id: Annotated[str | None, Query()] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return use_case.get_emerging_opportunities(
        vertical_id=vertical_id,
        limit=limit,
        offset=offset,
    )


@router.get("/declining_risks", response_model=List[TopPainOut])
def get_declining_risks(
    use_case: InsightsUseCase = Depends(get_insights_use_case),
    vertical_id: Annotated[str | None, Query()] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return use_case.get_declining_risks(
        vertical_id=vertical_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{cluster_id}", response_model=ClusterDetailOut)
def get_cluster_detail(cluster_id: str, use_case: InsightsUseCase = Depends(get_insights_use_case)):
    try:
        return use_case.get_cluster_detail(cluster_id=cluster_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{cluster_id}/build_hypothesis")
def generate_build_hypothesis(cluster_id: str, use_case: InsightsUseCase = Depends(get_insights_use_case)):
    try:
        return use_case.generate_build_hypothesis(cluster_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{cluster_id}/export", response_model=VentureOSExportPayloadV1Schema)
def export_ventureos_payload(cluster_id: str, use_case: InsightsUseCase = Depends(get_insights_use_case)):
    try:
        return use_case.export_ventureos_payload(cluster_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
