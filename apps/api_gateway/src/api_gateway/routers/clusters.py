from __future__ import annotations

from fastapi import APIRouter, Depends

from api_gateway.schemas.clusters import ClusterOut
from api_gateway.services.clusters_service import ClustersService
from api_gateway.dependencies import get_clusters_service

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=list[ClusterOut])
def list_clusters(service: ClustersService = Depends(get_clusters_service)) -> list[ClusterOut]:
    return service.list_clusters()


@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: str, service: ClustersService = Depends(get_clusters_service)) -> ClusterOut:
    return service.get_cluster(cluster_id)
