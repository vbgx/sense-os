from __future__ import annotations

import logging
from typing import Any, Iterable

from sense_queue.client import RedisJobQueueClient
from scheduler.jobs import asdict

log = logging.getLogger(__name__)


def _job_log_line(payload: dict[str, Any]) -> str:
    t = payload.get("type")
    q = payload.get("queue")
    rid = payload.get("run_id")
    vid = payload.get("vertical_id")
    vdb = payload.get("vertical_db_id")
    day = payload.get("day")
    src = payload.get("source")
    sources = payload.get("sources") or []
    sources_n = len(sources) if isinstance(sources, list) else 0
    query = payload.get("query")
    limit = payload.get("limit")
    return (
        f"type={t} queue={q} run_id={rid} vertical_id={vid} vertical_db_id={vdb} "
        f"day={day} source={src} sources_count={sources_n} query={query!r} limit={limit}"
    )


def publish_jobs(jobs: Iterable[Any]) -> int:
    client = RedisJobQueueClient()
    n = 0
    for j in jobs:
        payload = asdict(j)
        queue = payload.get("queue")
        if not isinstance(queue, str) or not queue:
            raise ValueError(f"Job missing queue: {payload!r}")

        # 🔥 log BEFORE publish so you see what was actually enqueued
        log.info("enqueue %s", _job_log_line(payload))

        client.publish(queue, payload)
        n += 1

    log.info("published_jobs=%s", n)
    return n
