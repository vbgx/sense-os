from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional

import redis

from sense_queue.worker_base import handle_job

log = logging.getLogger(__name__)


class RedisJobQueueClient:
    def __init__(self, redis_url: Optional[str] = None) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.r = redis.Redis.from_url(self.redis_url, decode_responses=True)

    def publish(self, queue: str, job: Dict[str, Any]) -> None:
        self.r.rpush(queue, json.dumps(job))

    def run(self, *, queue: str = "ingest", poll_timeout_s: int = 5) -> None:
        log.info("Worker loop started (queue=%s)", queue)
        while True:
            item = self.r.blpop(queue, timeout=poll_timeout_s)
            if not item:
                continue

            _key, raw = item
            try:
                job = json.loads(raw)
                if not isinstance(job, dict):
                    raise ValueError("job is not a dict")
            except Exception:
                log.exception("Invalid job payload: %r", raw)
                continue

            try:
                handled = handle_job(job)
                if not handled:
                    pass
            except Exception:
                log.exception("Job crashed: %r", job)
                time.sleep(0.2)
