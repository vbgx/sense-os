from __future__ import annotations

import logging
from typing import Any

from sense_queue.worker_base import Worker
from ingestion_worker.pipeline.ingest_vertical import ingest_vertical

log = logging.getLogger(__name__)


def _safe_int(x: Any) -> int:
    try:
        return int(x)
    except Exception:
        return 0


class IngestionWorker(Worker):
    def load(self, batch_ctx: dict[str, Any]):
        # job dict already contains everything
        return batch_ctx

    def process(self, items):
        # items is expected to be the job dict (not a list)
        if not isinstance(items, dict):
            raise TypeError(f"ingestion worker expected dict job, got {type(items)!r}")

        vertical_id = items.get("vertical_id")
        vertical_db_id = items.get("vertical_db_id")
        run_id = items.get("run_id")
        day = items.get("day")
        source = items.get("source")
        sources = items.get("sources") or []
        sources_n = len(sources) if isinstance(sources, list) else 0
        query = items.get("query")
        limit = items.get("limit")

        log.info(
            "ingest_job_received vertical_id=%s vertical_db_id=%s run_id=%s day=%s source=%s sources_count=%s query=%r limit=%s",
            vertical_id,
            vertical_db_id,
            run_id,
            day,
            source,
            sources_n,
            query,
            limit,
        )

        out = ingest_vertical(items) or {}
        # Normalize common fields
        fetched = _safe_int(out.get("fetched"))
        inserted = _safe_int(out.get("inserted") or out.get("persisted"))
        skipped_db = _safe_int(out.get("skipped_db") or out.get("skipped"))
        failed_sources = _safe_int(out.get("failed_sources"))
        skipped_sources = _safe_int(out.get("skipped_sources"))
        skipped_items = _safe_int(out.get("skipped_items"))

        log.info(
            "ingest_job_done vertical_id=%s vertical_db_id=%s run_id=%s day=%s fetched=%s inserted=%s skipped_db=%s failed_sources=%s skipped_sources=%s skipped_items=%s",
            vertical_id,
            vertical_db_id,
            run_id,
            day,
            fetched,
            inserted,
            skipped_db,
            failed_sources,
            skipped_sources,
            skipped_items,
        )
        return out

    def persist(self, outputs):
        # ingest_vertical persists already
        return None
