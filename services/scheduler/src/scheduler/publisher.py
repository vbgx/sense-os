from __future__ import annotations

import logging
from typing import Any, Iterable

from sense_queue.client import RedisJobQueueClient
from scheduler.jobs import asdict

log = logging.getLogger(__name__)


def publish_jobs(jobs: Iterable[Any]) -> int:
    client = RedisJobQueueClient()
    n = 0
    for j in jobs:
        payload = asdict(j)
        queue = payload.get("queue")
        if not isinstance(queue, str) or not queue:
            raise ValueError(f"Job missing queue: {payload!r}")
        client.publish(queue, payload)
        n += 1
    log.info("published_jobs=%s", n)
    return n
