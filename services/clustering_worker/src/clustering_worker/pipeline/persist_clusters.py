from __future__ import annotations

from typing import Any

from clustering_worker.clustering.summary import SummaryInputs, synthesize_cluster_summary
from clustering_worker.storage.clusters_writer import ClustersWriter


def _extract_representative_texts(cluster: dict[str, Any]) -> list[str]:
    """
    Try to extract representative texts from whatever structure we have.
    v1: supports common shapes:
      - cluster["representative_signals"] as list[{"text": "..."}] or list[str]
      - cluster["signals"] list[{"text": "..."}]
      - cluster["title_candidates"] list[str]
    """
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
    """
    Enrich clusters with cluster_summary and persist.
    """
    enriched: list[dict[str, Any]] = []
    for c in clusters_payload:
        dominant_persona = c.get("dominant_persona")
        # if you already compute top ngrams upstream, pass them here.
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
        enriched.append(c)

    writer.write_clusters(enriched)
