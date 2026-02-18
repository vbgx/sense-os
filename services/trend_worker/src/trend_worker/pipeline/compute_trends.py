from __future__ import annotations

from typing import Any

from trend_worker.pipeline.aggregate_daily import aggregate_daily
from trend_worker.metrics import (
    breakout,
    declining,
    emerging,
    half_life,
    opportunity_window,
    saturation,
    velocity,
    volatility,
)
from trend_worker.pipeline.persist_metrics import persist_metrics
from trend_worker.pipeline.persist_timeline import persist_timeline


def compute_trends(job: dict[str, Any]) -> dict[str, Any]:
    vertical_db_id = int(job["vertical_db_id"])
    taxonomy_version = str(job["taxonomy_version"])

    daily_history = aggregate_daily(
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
    )

    metrics_payload = []
    for cluster_id, history in daily_history.items():
        metrics_payload.append(
            {
                "cluster_id": cluster_id,
                "vertical_db_id": vertical_db_id,
                "taxonomy_version": taxonomy_version,
                "breakout_score": breakout.compute(history),
                "declining_score": declining.compute(history),
                "emerging_score": emerging.compute(history),
                "half_life_days": half_life.compute(history),
                "opportunity_window_score": opportunity_window.compute(history),
                "saturation_score": saturation.compute(history),
                "velocity_score": velocity.compute(history),
                "volatility_score": volatility.compute(history),
            }
        )

    persist_metrics(metrics_payload)
    persist_timeline(metrics_payload)

    return {
        "clusters": len(metrics_payload),
        "vertical_db_id": vertical_db_id,
        "taxonomy_version": taxonomy_version,
    }


def compute_trends_job(job: dict[str, Any]) -> dict[str, Any]:
    return compute_trends(job)
