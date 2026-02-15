from __future__ import annotations

from datetime import date
import logging
from typing import Any, Dict

from trend_worker.pipeline.compute_trends import compute_trends_job

log = logging.getLogger(__name__)


def compute_daily_metrics(*, day: date, job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute and persist daily trend metrics for a given day.
    """
    # Ensure deterministic day
    job = dict(job)
    job["day"] = day.isoformat()

    res = compute_trends_job(job)

    # Keep "trend_job" in message for validate_full_boot.sh grep
    log.info(
        "trend_job day=%s rows=%s upserted=%s",
        res.get("day"),
        res.get("rows"),
        res.get("upserted"),
    )
    return res
