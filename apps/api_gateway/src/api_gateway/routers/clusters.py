from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api_gateway.schemas.clusters import ClusterOut
from api_gateway.services.clusters_service import ClustersService
from api_gateway.dependencies import get_clusters_service

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=list[ClusterOut])
def list_clusters(
    service: ClustersService = Depends(get_clusters_service),
    min_exploitability: int | None = Query(default=None, ge=0, le=100),
    max_exploitability: int | None = Query(default=None, ge=0, le=100),
    order_by: str | None = Query(default=None, description="Supported: exploitability_score"),
    desc: bool = Query(default=True),
) -> list[ClusterOut]:
    return service.list_clusters(
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
        order_by=order_by,
        desc=desc,
    )


@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: str, service: ClustersService = Depends(get_clusters_service)) -> ClusterOut:
    return service.get_cluster(cluster_id)
