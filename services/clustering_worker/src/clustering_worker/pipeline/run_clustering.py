from __future__ import annotations

from typing import Any

from clustering_worker.pipeline.build_vectors import build_vectors
from clustering_worker.pipeline.load_instances import load_instances
from clustering_worker.clustering.merge import cluster_vectors
from clustering_worker.pipeline.persist_clusters import persist_clusters
from clustering_worker.clustering.representative import attach_representative_signals
from clustering_worker.clustering.keyphrases import extract_key_phrases_from_signals
from clustering_worker.clustering.confidence import ConfidenceInputs, compute_confidence_score


def _coerce_signal_id(inst: dict[str, Any], *, fallback: int) -> str:
    for k in ("source_external_id", "external_id", "id", "signal_id"):
        v = inst.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, int):
            return str(v)
    return str(fallback)


def _cluster_instances(instances: list[dict[str, Any]]) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    for idx, inst in enumerate(instances):
        content = inst.get("content") or inst.get("text") or inst.get("body") or ""
        signals.append(
            {
                "id": _coerce_signal_id(inst, fallback=idx + 1),
                "text": content,
                "content": content,
                "source": inst.get("source"),
            }
        )

    cluster = {
        "title": "All pains",
        "size": len(signals),
        "signals": signals,
    }
    cluster = attach_representative_signals(cluster, k=5, per_user_cap=1)
    reps = cluster.get("representative_signals") or []
    cluster["representative_ids"] = cluster.get("top_signal_ids") or [
        s.get("id") for s in reps if isinstance(s, dict)
    ]
    cluster["key_phrases"] = extract_key_phrases_from_signals(reps, top_k=10)
    cluster["confidence_score"] = compute_confidence_score(
        ConfidenceInputs(
            size=len(signals),
            intra_similarity=None,
            silhouette_score=None,
            noise_ratio=None,
        )
    )
    return {"clusters": [cluster]}


def run_clustering(job: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    if isinstance(job, list):
        return _cluster_instances(job)

    vertical_db_id = int(job.get("vertical_db_id") or 1)
    taxonomy_version = str(job.get("taxonomy_version") or "v1")
    cache_dir = job.get("cache_dir")
    emit_json_event = bool(job.get("emit_json_event"))

    instances = load_instances(job)
    instance_ids, vectors, _ = build_vectors(
        {"emit_json_event": emit_json_event},
        instances,
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
        "pain_instances": len(instance_ids),
        "clusters": int((stats or {}).get("clusters") or 0),
        "links_inserted": int((stats or {}).get("links_inserted") or 0),
        "skipped": int((stats or {}).get("skipped") or 0),
        "vertical_db_id": vertical_db_id,
        "taxonomy_version": taxonomy_version,
    }


def run_clustering_job(job: dict[str, Any]) -> dict[str, Any]:
    return run_clustering(job)
