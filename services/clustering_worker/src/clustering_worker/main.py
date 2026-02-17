from __future__ import annotations

import logging
from typing import Any

from sense_queue.client import RedisJobQueueClient
from sense_queue.worker_base import job_handler

from clustering_worker.pipeline.run_clustering import run_clustering_job

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("clustering-worker")


@job_handler("cluster_vertical")
def handle_cluster_vertical(job: dict[str, Any]) -> None:
    run_clustering_job(job)
    log.info(
        "cluster_job vertical_id=%s vertical_db_id=%s run_id=%s day=%s cluster_version=%s",
        job.get("vertical_id"),
        job.get("vertical_db_id"),
        job.get("run_id"),
        job.get("day"),
        job.get("cluster_version"),
    )


def main() -> None:
    log.info("Clustering worker booted")
    client = RedisJobQueueClient()
    client.run(queue="cluster")


if __name__ == "__main__":
    main()
