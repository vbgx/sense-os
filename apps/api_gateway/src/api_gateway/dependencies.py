from __future__ import annotations

from typing import Generator

from fastapi import Depends

from db.session import get_session
from db.repos.pain_clusters import PainClustersRepo
from api_gateway.services.clusters_service import ClustersService


def get_db() -> Generator:
    yield from get_session()


def get_clusters_service(session=Depends(get_db)) -> ClustersService:
    return ClustersService(repo=PainClustersRepo(session=session))
