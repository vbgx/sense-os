from __future__ import annotations

from typing import Any, Dict, List

from ingestion_worker.adapters.hackernews.adapter import HNAdapterConfig, ingest_hackernews
from ingestion_worker.adapters.hackernews.client import HackerNewsClient


def fetch_hackernews_signals(
    *,
    vertical_id: str,
    vertical_db_id: int | None,
    taxonomy_version: str | None,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    client = HackerNewsClient()
    cfg = HNAdapterConfig(
        kinds=("ask", "show"),
        max_stories=int(limit),
        max_comments_per_story=30,
    )
    out: List[Dict[str, Any]] = []
    for d in ingest_hackernews(
        client=client,
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        cfg=cfg,
    ):
        if d.get("content"):
            out.append(d)
    return out
