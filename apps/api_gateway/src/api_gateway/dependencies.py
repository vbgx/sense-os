from __future__ import annotations

from fastapi import Depends

from db.session import get_session
from db.repos.pain_clusters import PainClustersRepo
from api_gateway.services.clusters_service import ClustersService


def get_clusters_service(session=Depends(get_session)) -> ClustersService:
    return ClustersService(repo=PainClustersRepo(session=session))
