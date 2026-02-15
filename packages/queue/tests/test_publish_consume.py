from __future__ import annotations

import json
import os
import time

import redis  # type: ignore

from sense_queue.contracts import validate_job


def test_publish_consume_roundtrip():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    qname = "test_queue_roundtrip"

    r = redis.Redis.from_url(redis_url, decode_responses=True)
    r.delete(qname)

    payload = {"type": "hello", "queue": qname, "run_id": "r1"}
    validate_job(payload)  # contract must accept

    r.lpush(qname, json.dumps(payload))
    item = r.blpop(qname, timeout=3)
    assert item is not None

    _, raw = item
    got = json.loads(raw)
    assert got["type"] == "hello"
    assert got["run_id"] == "r1"
