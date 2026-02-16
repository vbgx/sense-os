from __future__ import annotations

from typing import Any

from db.session import session_scope
from db.models import PainCluster


class ClustersWriter:
    """
    Persists clusters into DB.
    Assumes PainCluster ORM exists in packages/db.
    """

    def write_clusters(self, clusters: list[dict[str, Any]]) -> None:
        with session_scope() as s:
            for payload in clusters:
                cluster_id = payload.get("cluster_id") or payload.get("id")
                if cluster_id is None:
                    continue

                obj = s.get(PainCluster, cluster_id)
                if obj is None:
                    obj = PainCluster(id=cluster_id)
                    s.add(obj)

                if "cluster_summary" in payload:
                    obj.cluster_summary = payload["cluster_summary"]
