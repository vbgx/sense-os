from __future__ import annotations

import logging
from typing import Any

from ingestion_worker.adapters.reddit.fetch import fetch_reddit_signals
from ingestion_worker.adapters.hackernews.fetch_signals import fetch_hackernews_signals
from ingestion_worker.adapters.indiehackers.fetch_signals import fetch_indiehackers_signals
from ingestion_worker.adapters.producthunt.fetch_signals import fetch_producthunt_signals
from ingestion_worker.storage.signals_writer import SignalsWriter

log = logging.getLogger(__name__)


def ingest_vertical(job: dict[str, Any]) -> dict[str, int]:
    vertical_id = int(job["vertical_id"])
    source = str(job.get("source") or "reddit")
    query = str(job.get("query") or "saas")
    limit = int(job.get("limit") or 25)

    if source == "reddit":
        signals = fetch_reddit_signals(vertical_id=vertical_id, query=query, limit=limit)
    elif source == "hackernews":
        signals = fetch_hackernews_signals(vertical_id=vertical_id, limit=limit)
    elif source == "indiehackers":
        signals = fetch_indiehackers_signals(vertical_id=vertical_id, limit=limit)
    elif source == "producthunt":
        signals = fetch_producthunt_signals(vertical_id=vertical_id, limit=limit)
    else:
        raise ValueError(f"Unsupported ingestion source: {source}")

    writer = SignalsWriter()
    inserted, deduped = writer.insert_many(signals)

    return {"fetched": len(signals), "inserted": inserted, "skipped": deduped}
