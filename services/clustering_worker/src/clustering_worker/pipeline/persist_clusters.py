from __future__ import annotations

import json
from typing import Any

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


def persist_clusters(writer: ClustersWriter, clusters_payload: list[dict[str, Any]]) -> None:
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
