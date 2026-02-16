from __future__ import annotations

import json
from typing import Any

from clustering_worker.clustering.representative import attach_representative_signals
from clustering_worker.clustering.summary import SummaryInputs, synthesize_cluster_summary
from clustering_worker.storage.clusters_writer import ClustersWriter


def _extract_representative_texts(cluster: dict[str, Any]) -> list[str]:
    texts: list[str] = []

    reps = cluster.get("representative_signals") or []
    if isinstance(reps, list):
        for item in reps[:12]:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                t = item.get("text") or item.get("content") or item.get("body")
                if isinstance(t, str) and t.strip():
                    texts.append(t)

    if not texts:
        sigs = cluster.get("signals") or []
        if isinstance(sigs, list):
            for item in sigs[:12]:
                if isinstance(item, dict):
                    t = item.get("text") or item.get("content") or item.get("body")
                    if isinstance(t, str) and t.strip():
                        texts.append(t)

    if not texts:
        tcs = cluster.get("title_candidates") or []
        if isinstance(tcs, list):
            for s in tcs[:6]:
                if isinstance(s, str) and s.strip():
                    texts.append(s)

    return texts


def persist_clusters(writer: ClustersWriter, clusters_payload: list[dict[str, Any]]) -> None:
    enriched: list[dict[str, Any]] = []

    for c in clusters_payload:
        # 04.02 — compute representative signals + ids
        c = attach_representative_signals(c, k=5, per_user_cap=1)

        # 04.01 — compute summary (can use representative_signals now)
        dominant_persona = c.get("dominant_persona")
        top_ngrams = c.get("top_ngrams") or c.get("ngrams") or None
        rep_texts = _extract_representative_texts(c)

        summary = synthesize_cluster_summary(
            SummaryInputs(
                representative_texts=rep_texts,
                dominant_persona=dominant_persona,
                top_ngrams=top_ngrams if isinstance(top_ngrams, list) else None,
            )
        )

        c = dict(c)
        c["cluster_summary"] = summary

        # normalize persistence payload for DB writer
        top_ids = c.get("top_signal_ids")
        if isinstance(top_ids, list):
            c["top_signal_ids_json"] = json.dumps(top_ids)

        enriched.append(c)

    writer.write_clusters(enriched)
