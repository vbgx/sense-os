from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional

import redis

from sense_queue.worker_base import handle_job
from sense_queue.retry import RetryPolicy

log = logging.getLogger(__name__)


class RedisJobQueueClient:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        *,
        retry_policy: Optional[RetryPolicy] = None,
        retry_zset_suffix: str = ":retry",
        dlq_suffix: str = ":dlq",
        retry_batch_size: int = 50,
    ) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.r = redis.Redis.from_url(self.redis_url, decode_responses=True)
        self.retry_policy = retry_policy or RetryPolicy()
        self.retry_zset_suffix = retry_zset_suffix
        self.dlq_suffix = dlq_suffix
        self.retry_batch_size = retry_batch_size

    def publish(self, queue: str, job: Dict[str, Any]) -> None:
        self.r.rpush(queue, json.dumps(job))

    def _retry_key(self, queue: str) -> str:
        return f"{queue}{self.retry_zset_suffix}"

    def _dlq_key(self, queue: str) -> str:
        return f"{queue}{self.dlq_suffix}"

    def _drain_retry_queue(self, queue: str) -> int:
        retry_key = self._retry_key(queue)
        now = time.time()
        items = self.r.zrangebyscore(retry_key, 0, now, start=0, num=self.retry_batch_size)
        if not items:
            return 0
        pipe = self.r.pipeline()
        pipe.rpush(queue, *items)
        pipe.zrem(retry_key, *items)
        pipe.execute()
        return len(items)

    def _schedule_retry(self, queue: str, job: Dict[str, Any], err: Exception) -> None:
        attempt = int(job.get("_attempt", 0)) + 1
        job["_attempt"] = attempt
        job["_error"] = str(err)
        job["_error_type"] = type(err).__name__
        job["_error_ts"] = time.time()

        if self.retry_policy and self.retry_policy.should_retry(attempt=attempt):
            delay = self.retry_policy.next_delay_s(attempt=attempt)
            score = time.time() + delay
            retry_key = self._retry_key(queue)
            self.r.zadd(retry_key, {json.dumps(job): score})
            log.warning(
                "Job failed, scheduled retry attempt=%s delay_s=%.2f queue=%s",
                attempt,
                delay,
                queue,
            )
        else:
            dlq_key = self._dlq_key(queue)
            self.r.rpush(dlq_key, json.dumps(job))
            log.error("Job failed, moved to DLQ attempt=%s queue=%s", attempt, queue)

    def run(self, *, queue: str = "ingest", poll_timeout_s: int = 5) -> None:
        log.info("Worker loop started (queue=%s)", queue)
        while True:
            self._drain_retry_queue(queue)
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
            except Exception as exc:
                log.exception("Job crashed: %r", job)
                self._schedule_retry(queue, job, exc)
