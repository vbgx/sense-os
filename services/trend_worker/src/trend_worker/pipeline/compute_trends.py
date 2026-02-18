from __future__ import annotations

from typing import Any

from trend_worker import daily_metrics


def compute_trends(job: dict[str, Any]) -> dict[str, Any]:
    return daily_metrics.compute_trends_job(job)


def compute_trends_job(job: dict[str, Any]) -> dict[str, Any]:
    return compute_trends(job)
