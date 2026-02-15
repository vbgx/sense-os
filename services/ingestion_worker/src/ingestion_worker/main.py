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

    fetched = int(result.get("fetched", 0) or 0)
    inserted = int(result.get("inserted", 0) or 0)
    skipped = int(result.get("skipped", 0) or 0)

    log.info(
        "Ingested vertical_id=%s source=%s run_id=%s fetched=%s inserted=%s skipped=%s",
        job.get("vertical_id"),
        job.get("source"),
        job.get("run_id"),
        fetched,
        inserted,
        skipped,
    )


def main() -> None:
    log.info("Ingestion worker booted")
    client = RedisJobQueueClient()
    client.run(queue="ingest")


if __name__ == "__main__":
    main()
