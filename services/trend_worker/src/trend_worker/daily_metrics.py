from __future__ import annotations

from datetime import date
from typing import Any, Dict

from trend_worker.pipeline.compute_trends import compute_trends_job


def compute_daily_metrics(*, day: date, job: Dict[str, Any]) -> None:
    # Ensure deterministic day
    job = dict(job)
    job["day"] = day.isoformat()

    res = compute_trends_job(job)

    # IMPORTANT: stdout log for validate_full_boot.sh grep
    print(f"trend_job day={res.get('day')} rows={res.get('rows')} upserted={res.get('upserted')}")
