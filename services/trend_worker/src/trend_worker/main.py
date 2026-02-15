from __future__ import annotations

import json
import logging
import os
from datetime import date, timedelta
from typing import Any, Dict, Tuple

import redis  # type: ignore

from sense_queue.contracts import validate_job
from trend_worker.daily_metrics import compute_daily_metrics

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE = os.getenv("TREND_QUEUE") or os.getenv("QUEUE_TREND") or "trend"
CLUSTER_VERSION = os.getenv("CLUSTER_VERSION", "tfidf_v1")
FORMULA_VERSION = os.getenv("FORMULA_VERSION", "formula_v1")

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("trend-worker")


def _parse_day(s) -> date:
    if s in (None, "", "None"):
        return date.today() - timedelta(days=1)
    return date.fromisoformat(str(s))


def _extract_counts(result: Any) -> Tuple[int | None, int | None]:
    """
    Best-effort: if compute_daily_metrics returns counts, surface them.
    Supports dict or tuple-like returns.
    """
    if isinstance(result, dict):
        computed = result.get("computed") or result.get("computed_trends") or result.get("rows")
        upserted = result.get("upserted")
        return (int(computed) if computed is not None else None, int(upserted) if upserted is not None else None)
    if isinstance(result, tuple) and len(result) >= 2:
        a, b = result[0], result[1]
        return (int(a) if a is not None else None, int(b) if b is not None else None)
    return (None, None)


def consume_trend_job(job_raw: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Validate and consume a trend_job payload.
    """
    job = validate_job(job_raw)

    job_type = str(job.type)
    if job_type not in ("trend_job", "trend_day"):
        log.info("trend_skip unsupported type=%s payload_keys=%s", job_type, list(job_raw.keys()))
        return {"skipped": 1, "reason": "unsupported_type"}

    day = _parse_day(job.day or job_raw.get("day"))

    payload = dict(job_raw)
    payload["type"] = "trend_job"
    payload["day"] = day.isoformat()
    payload.setdefault("cluster_version", CLUSTER_VERSION)
    payload.setdefault("formula_version", FORMULA_VERSION)

    result = compute_daily_metrics(day=day, job=payload)
    computed, upserted = _extract_counts(result)

    log.info(
        "trend_job day=%s vertical_id=%s cluster_version=%s formula_version=%s computed=%s upserted=%s",
        day.isoformat(),
        payload.get("vertical_id"),
        payload.get("cluster_version"),
        payload.get("formula_version"),
        computed,
        upserted,
    )
    return result


def main() -> None:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    log.info("Trend worker started (queue=%s)", QUEUE)

    while True:
        item = r.blpop(QUEUE, timeout=2)
        if not item:
            continue

        _, raw = item
        job_raw: Dict[str, Any] = json.loads(raw)

        try:
            consume_trend_job(job_raw)
        except Exception:
            log.exception("trend_job failed payload=%s", job_raw)


if __name__ == "__main__":
    main()
