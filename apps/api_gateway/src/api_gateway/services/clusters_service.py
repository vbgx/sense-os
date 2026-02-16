from __future__ import annotations

import json
from dataclasses import dataclass

from db.repos.pain_clusters import PainClustersRepo


def _to_int(v, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


@dataclass
class ClustersService:
    repo: PainClustersRepo

    def list_clusters(
        self,
        *,
        vertical_id: int | None = None,
        min_exploitability: int | None = None,
        max_exploitability: int | None = None,
        order_by: str | None = None,
        desc: bool = True,
    ):
        rows = self.repo.list()

        # hydrate persona distribution (existing behavior)
        for r in rows:
            r.persona_distribution = self._parse_dist(getattr(r, "persona_distribution_json", "{}"))

        # filtering (v1) — done in service to avoid guessing repo SQL API
        if vertical_id is not None:
            rows = [r for r in rows if _to_int(getattr(r, "vertical_id", 0)) == int(vertical_id)]
        if min_exploitability is not None:
            rows = [r for r in rows if _to_int(getattr(r, "exploitability_score", 0)) >= int(min_exploitability)]
        if max_exploitability is not None:
            rows = [r for r in rows if _to_int(getattr(r, "exploitability_score", 0)) <= int(max_exploitability)]

        # sorting (supported: exploitability_score)
        if order_by is not None:
            key = order_by.strip()
            if key == "exploitability_score":
                rows = sorted(
                    rows,
                    key=lambda r: _to_int(getattr(r, "exploitability_score", 0)),
                    reverse=bool(desc),
                )

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
