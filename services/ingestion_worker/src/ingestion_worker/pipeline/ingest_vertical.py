from __future__ import annotations

import logging
from typing import Any

from ingestion_worker.adapters.reddit.fetch import fetch_reddit_signals
from ingestion_worker.storage.signals_writer import SignalsWriter

log = logging.getLogger(__name__)


def ingest_vertical(job: dict[str, Any]) -> dict[str, int]:
    """Fetch signals for a vertical and persist them, returning a summary."""
    vertical_id = int(job["vertical_id"])
    source = str(job.get("source") or "reddit")
    query = str(job.get("query") or "saas")
    limit = int(job.get("limit") or 25)

    log.info("Fetching signals vertical_id=%s source=%s query=%s limit=%s", vertical_id, source, query, limit)

    signals = fetch_reddit_signals(vertical_id=vertical_id, query=query, limit=limit)

    writer = SignalsWriter()
    inserted, deduped = writer.insert_many(signals)

    log.info(
        "Ingestion persisted vertical_id=%s source=%s inserted=%s deduped=%s",
        vertical_id,
        source,
        inserted,
        deduped,
    )
    return {"fetched": len(signals), "inserted": inserted, "skipped": deduped}
