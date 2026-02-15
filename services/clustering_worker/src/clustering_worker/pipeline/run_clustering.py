from __future__ import annotations

import logging
from typing import Any

from db.session import SessionLocal
from db.models import PainInstance
from db.repos import pain_clusters as clusters_repo
from db.repos import cluster_signals as cluster_signals_repo

log = logging.getLogger(__name__)


def run_clustering_job(job: dict[str, Any]) -> dict[str, int]:
    """
    V0 clustering (minimal, deterministic):
    - Creates/updates ONE cluster per vertical for a given cluster_version.
    - Links ALL pain_instances (for that vertical) to that cluster.
    This is enough to unblock trend-worker + end-to-end validation.
    """
    vertical_id = int(job.get("vertical_id") or 0)
    if vertical_id <= 0:
        raise ValueError(f"invalid vertical_id: {job.get('vertical_id')!r}")

    cluster_version = str(job.get("cluster_version") or "tfidf_v1")

    db = SessionLocal()
    try:
        ids = [
            int(x[0])
            for x in db.query(PainInstance.id)
            .filter(PainInstance.vertical_id == vertical_id)
            .order_by(PainInstance.id.asc())
            .all()
        ]

        cluster_key = "all"
        title = "All pains"
        size = len(ids)

        cluster_obj, _created = clusters_repo.upsert_cluster(
            db,
            vertical_id=vertical_id,
            cluster_version=cluster_version,
            cluster_key=cluster_key,
            title=title,
            size=size,
        )

        inserted = cluster_signals_repo.link_many(db, cluster_id=int(cluster_obj.id), pain_instance_ids=ids)
        db.commit()

        log.info(
            "clustered vertical_id=%s cluster_version=%s clusters=1 pain_instances=%s links_inserted=%s",
            vertical_id,
            cluster_version,
            size,
            inserted,
        )
        return {"clusters": 1, "pain_instances": size, "links_inserted": inserted}
    finally:
        db.close()
