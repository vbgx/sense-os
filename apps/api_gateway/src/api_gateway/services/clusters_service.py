from __future__ import annotations

from dataclasses import dataclass

from db.repos.pain_clusters import PainClustersRepo


@dataclass
class ClustersService:
    repo: PainClustersRepo

    def list_clusters(self):
        return self.repo.list()

    def get_cluster(self, cluster_id: str):
        return self.repo.get(cluster_id)
