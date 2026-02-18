from __future__ import annotations

from typing import Any

from clustering_worker.pipeline.build_vectors import build_vectors
from clustering_worker.pipeline.load_instances import load_instances
from clustering_worker.clustering.merge import cluster_vectors
from clustering_worker.pipeline.persist_clusters import persist_clusters


def run_clustering(job: dict[str, Any]) -> dict[str, Any]:
    vertical_db_id = int(job.get("vertical_db_id") or 1)
    taxonomy_version = str(job.get("taxonomy_version") or "v1")
    cache_dir = job.get("cache_dir")
    emit_json_event = bool(job.get("emit_json_event"))

    instances = load_instances(job)
    instance_ids, vectors, _ = build_vectors(
        job={"emit_json_event": emit_json_event},
        instances=instances,
        cache_dir=str(cache_dir) if cache_dir else None,
    )

    labels = cluster_vectors(vectors, params={"similarity_threshold": float(job.get("similarity_threshold") or 0.82)})
    stats = persist_clusters(
        {
            "vertical_db_id": vertical_db_id,
            "taxonomy_version": taxonomy_version,
            **job,
        },
        instance_ids,
        labels,
    )

    return {
        "instances": len(instance_ids),
        "clusters": int(stats.get("clusters") or 0),
        "vertical_db_id": vertical_db_id,
        "taxonomy_version": taxonomy_version,
    }


def run_clustering_job(job: dict[str, Any]) -> dict[str, Any]:
    return run_clustering(job)
