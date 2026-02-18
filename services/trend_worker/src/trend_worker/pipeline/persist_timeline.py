from __future__ import annotations

from typing import Any

from trend_worker.pipeline.persist_timeline_from_metrics import persist_timeline_from_metrics


def persist_timeline(metrics_payload: list[dict[str, Any]]) -> None:
    persist_timeline_from_metrics(metrics_payload)
