from __future__ import annotations

import json
from dataclasses import dataclass

from db.repos.pain_clusters import PainClustersRepo


@dataclass
class ClustersService:
    repo: PainClustersRepo

    def list_clusters(self):
        rows = self.repo.list()
        for r in rows:
            r.persona_distribution = self._parse_dist(getattr(r, "persona_distribution_json", "{}"))
        return rows

    def get_cluster(self, cluster_id: str):
        r = self.repo.get(cluster_id)
        r.persona_distribution = self._parse_dist(getattr(r, "persona_distribution_json", "{}"))
        return r

    @staticmethod
    def _parse_dist(s: str) -> dict[str, float]:
        try:
            obj = json.loads(s or "{}")
            if isinstance(obj, dict):
                return {str(k): float(v) for k, v in obj.items()}
        except Exception:
            pass
        return {}
