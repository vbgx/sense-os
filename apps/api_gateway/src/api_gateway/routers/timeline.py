from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api_gateway.schemas.timeline import TimelinePointOut
from api_gateway.dependencies import get_clusters_use_case
from application.use_cases.clusters import ClustersUseCase

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("/{cluster_id}/timeline", response_model=list[TimelinePointOut])
def get_cluster_timeline(
    cluster_id: str,
    days: int = Query(default=90, ge=1, le=3650),
    use_case: ClustersUseCase = Depends(get_clusters_use_case),
) -> list[TimelinePointOut]:
    rows = use_case.list_cluster_timeline(cluster_id=cluster_id, days=days)
    return [
        TimelinePointOut(
            date=r.day,
            volume=r.volume,
            growth_rate=r.growth_rate,
            velocity=r.velocity,
            breakout_flag=r.breakout_flag,
        )
        for r in rows
    ]
