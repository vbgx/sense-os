from __future__ import annotations

import json
import os
from datetime import date, timedelta
from typing import Any, Dict, Tuple

import redis  # type: ignore

from sense_queue.contracts import validate_job
from trend_worker.daily_metrics import compute_daily_metrics

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE = os.getenv("QUEUE_TREND", "trend")


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
        computed = result.get("computed") or result.get("computed_trends")
        upserted = result.get("upserted")
        return (int(computed) if computed is not None else None, int(upserted) if upserted is not None else None)
    if isinstance(result, tuple) and len(result) >= 2:
        a, b = result[0], result[1]
        return (int(a) if a is not None else None, int(b) if b is not None else None)
    return (None, None)


def main() -> None:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    print(f"Trend worker started... queue={QUEUE}")

    while True:
        item = r.blpop(QUEUE, timeout=2)
        if not item:
            continue

        _, raw = item
        job_raw: Dict[str, Any] = json.loads(raw)

        # ✅ validate + normalize
        job = validate_job(job_raw)

        # ✅ strict routing
        if job.type != "trend_day":
            print(f"[trend] skip unsupported job.type={job.type} payload_keys={list(job_raw.keys())}")
            continue

        day = _parse_day(job.day)
        vertical_id = job.vertical_id

        # Compute + persist
        result = compute_daily_metrics(day=day, job=job_raw)

        computed, upserted = _extract_counts(result)
        if computed is not None or upserted is not None:
            print(
                f"[trend] type=trend_day day={day.isoformat()} vertical_id={vertical_id} "
                f"computed_trends={computed} upserted={upserted}"
            )
        else:
            print(
                f"[trend] type=trend_day day={day.isoformat()} vertical_id={vertical_id} done"
            )


if __name__ == "__main__":
    main()
