from __future__ import annotations

import json
from typing import Any, Iterable

from db.repos import cluster_signals as cluster_signals_repo
from db.repos import pain_clusters as pain_clusters_repo
from db.session import session_scope

from clustering_worker.clustering.representative import attach_representative_signals
from clustering_worker.clustering.keyphrases import extract_key_phrases_from_signals
from clustering_worker.clustering.summary import SummaryInputs, synthesize_cluster_summary
from clustering_worker.clustering.confidence import (
    ConfidenceInputs,
    compute_confidence_score,
)
from clustering_worker.storage.clusters_writer import ClustersWriter


def _extract_representative_texts(cluster: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    reps = cluster.get("representative_signals") or []
    if isinstance(reps, list):
        for item in reps[:12]:
            if isinstance(item, dict):
                t = item.get("text")
                if isinstance(t, str) and t.strip():
                    texts.append(t)
    return texts


def _persist_from_job(job: dict[str, Any], instance_ids: Iterable[int]) -> dict[str, int]:
    vertical_db_id = int(job.get("vertical_db_id") or 1)
    cluster_version = str(job.get("cluster_version") or "tfidf_v1")
    instance_ids = list(instance_ids)

    if not instance_ids:
        return {"clusters": 0, "links_inserted": 0, "pain_instances": 0, "skipped": 0}

    with session_scope() as db:
        if pain_clusters_repo.clusters_exist_for_version(
            db, vertical_id=vertical_db_id, cluster_version=cluster_version
        ):
            return {
                "clusters": 0,
                "links_inserted": 0,
                "pain_instances": len(instance_ids),
                "skipped": 1,
            }

        cluster, _ = pain_clusters_repo.upsert_cluster(
            db,
            vertical_id=vertical_db_id,
            cluster_version=cluster_version,
            cluster_key="all",
            title="All pains",
            size=len(instance_ids),
        )
        links = cluster_signals_repo.link_many(
            db,
            cluster_id=int(cluster.id),
            pain_instance_ids=instance_ids,
        )

        return {
            "clusters": 1,
            "links_inserted": int(links),
            "pain_instances": len(instance_ids),
            "skipped": 0,
        }


def persist_clusters(
    writer_or_job: ClustersWriter | dict[str, Any],
    clusters_payload: list[dict[str, Any]] | list[int],
    labels: list[int] | None = None,
) -> dict[str, int] | None:
    if isinstance(writer_or_job, ClustersWriter):
        writer = writer_or_job
        clusters_payload = clusters_payload or []
        enriched: list[dict[str, Any]] = []

        for c in clusters_payload:
            c = attach_representative_signals(c, k=5, per_user_cap=1)

            reps = c.get("representative_signals") or []
            key_phrases = extract_key_phrases_from_signals(reps, top_k=10)
            c = dict(c)
            c["key_phrases_json"] = json.dumps(key_phrases)

            # --- Confidence ---
            confidence = compute_confidence_score(
                ConfidenceInputs(
                    size=int(c.get("size", 0)),
                    intra_similarity=c.get("intra_similarity"),
                    silhouette_score=c.get("silhouette_score"),
                    noise_ratio=c.get("noise_ratio"),
                )
            )
            c["confidence_score"] = confidence

            # --- Summary ---
            summary = synthesize_cluster_summary(
                SummaryInputs(
                    representative_texts=_extract_representative_texts(c),
                    dominant_persona=c.get("dominant_persona"),
                    top_ngrams=c.get("top_ngrams"),
                )
            )
            c["cluster_summary"] = summary

            enriched.append(c)

        writer.write_clusters(enriched)
        return None

    job = writer_or_job
    instance_ids = [int(pid) for pid in (clusters_payload or [])]
    _ = labels
    return _persist_from_job(job, instance_ids)
