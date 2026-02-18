from __future__ import annotations

from typing import Any


def persist_timeline_from_metrics(metrics_payload: list[dict[str, Any]], **_: Any) -> None:
    return


def persist_timeline_from_trend_metrics(metrics_payload: list[dict[str, Any]] | None = None, **kwargs: Any) -> None:
    payload = metrics_payload if metrics_payload is not None else []
    _ = kwargs
    persist_timeline_from_metrics(payload)
