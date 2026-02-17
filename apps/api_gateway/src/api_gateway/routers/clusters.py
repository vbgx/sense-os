from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api_gateway.schemas.clusters import ClusterListOut, ClusterOut
from api_gateway.schemas.timeline import TimelinePointOut
from api_gateway.dependencies import get_clusters_use_case
from application.use_cases.clusters import ClustersUseCase

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=ClusterListOut)
def list_clusters(
    use_case: ClustersUseCase = Depends(get_clusters_use_case),
    vertical_id: int | None = Query(default=None),
    min_exploitability: int | None = Query(default=None, ge=0, le=100),
    max_exploitability: int | None = Query(default=None, ge=0, le=100),
    order_by: str | None = Query(default=None, description="Supported: exploitability_score"),
    desc: bool = Query(default=True),
) -> ClusterListOut:
    rows = use_case.list_clusters(
        vertical_id=vertical_id,
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
        order_by=order_by,
        desc=desc,
    )
    return ClusterListOut(total=len(rows), items=rows)


@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: str, use_case: ClustersUseCase = Depends(get_clusters_use_case)) -> ClusterOut:
    return use_case.get_cluster(cluster_id)


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
