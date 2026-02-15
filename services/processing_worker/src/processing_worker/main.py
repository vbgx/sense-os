from __future__ import annotations

import logging
from typing import Any

from sense_queue.client import RedisJobQueueClient
from sense_queue.worker_base import job_handler

from processing_worker.pipeline.process_batch import process_signals_batch

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("processing-worker")


@job_handler("process_signals")
def handle_process_signals(job: dict[str, Any]) -> None:
    res = process_signals_batch(job)

    signals_n = int(res.get("signals", 0) or 0)
    created_n = int(res.get("pain_instances_created", 0) or 0)
    skipped_n = int(res.get("pain_instances_skipped", 0) or 0)

    log.info(
        "Processed vertical_id=%s run_id=%s day=%s signals=%s",
        job.get("vertical_id"),
        job.get("run_id"),
        job.get("day"),
        signals_n,
    )
    log.info("pain_instances_created=%s", created_n)
    log.info("pain_instances_skipped=%s", skipped_n)


def main() -> None:
    log.info("Processing worker booted")
    client = RedisJobQueueClient()
    client.run(queue="process")


if __name__ == "__main__":
    main()
