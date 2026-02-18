from __future__ import annotations

import logging
from typing import Any

from sense_queue.client import RedisJobQueueClient
from sense_queue.worker_base import job_handler

from ingestion_worker.pipeline.ingest_vertical import ingest_vertical


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("ingestion-worker")


@job_handler("ingest_vertical")
def handle_ingest_vertical(job: dict[str, Any]) -> None:
    result = ingest_vertical(job)

    sources = int(result.get("sources", 0) or 0)
    sources_ok = int(result.get("sources_ok", 0) or 0)
    sources_err = int(result.get("sources_err", 0) or 0)
    raw = int(result.get("signals_raw", 0) or 0)
    deduped = int(result.get("signals_deduped", 0) or 0)

    log.info(
        "Ingested vertical_id=%s vertical_db_id=%s sources=%s ok=%s err=%s raw=%s deduped=%s run_id=%s day=%s",
        job.get("vertical_id"),
        job.get("vertical_db_id"),
        sources,
        sources_ok,
        sources_err,
        raw,
        deduped,
        job.get("run_id"),
        job.get("day") or job.get("start_day"),
    )


def main() -> None:
    log.info("Ingestion worker booted")
    client = RedisJobQueueClient()
    client.run(queue="ingest")


if __name__ == "__main__":
    main()
