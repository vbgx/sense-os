from __future__ import annotations

import json
from dataclasses import dataclass

from application.ports import UnitOfWork


def _to_int(v, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


def _parse_dist(s: str) -> dict[str, float]:
    try:
        obj = json.loads(s or "{}")
        if isinstance(obj, dict):
            return {str(k): float(v) for k, v in obj.items()}
    except Exception:
        pass
    return {}


@dataclass
class ClustersUseCase:
    uow: UnitOfWork

    def list_clusters(
        self,
        *,
        vertical_id: int | None = None,
        min_exploitability: int | None = None,
        max_exploitability: int | None = None,
        order_by: str | None = None,
        desc: bool = True,
    ):
        with self.uow:
            rows = self.uow.pain_clusters.list()

        for r in rows:
            setattr(r, "persona_distribution", _parse_dist(getattr(r, "persona_distribution_json", "{}")))

        if vertical_id is not None:
            rows = [r for r in rows if _to_int(getattr(r, "vertical_id", 0)) == int(vertical_id)]
        if min_exploitability is not None:
            rows = [r for r in rows if _to_int(getattr(r, "exploitability_score", 0)) >= int(min_exploitability)]
        if max_exploitability is not None:
            rows = [r for r in rows if _to_int(getattr(r, "exploitability_score", 0)) <= int(max_exploitability)]

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
        with self.uow:
            r = self.uow.pain_clusters.get(cluster_id)
        setattr(r, "persona_distribution", _parse_dist(getattr(r, "persona_distribution_json", "{}")))
        return r

    def list_cluster_timeline(self, *, cluster_id: str, days: int):
        with self.uow:
            return self.uow.cluster_daily_history.list_cluster_history(cluster_id=cluster_id, days=days)
