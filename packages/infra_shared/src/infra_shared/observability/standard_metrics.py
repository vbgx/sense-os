from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infra_shared.observability.metrics import metrics


@dataclass(frozen=True)
class MetricLabels:
    worker: str


def job_duration_seconds(labels: MetricLabels, seconds: float) -> None:
    metrics.timing(f"job_duration_seconds{{worker={labels.worker}}}", seconds)


def items_loaded_total(labels: MetricLabels, n: int) -> None:
    metrics.incr(f"items_loaded_total{{worker={labels.worker}}}", n)


def items_processed_total(labels: MetricLabels, n: int) -> None:
    metrics.incr(f"items_processed_total{{worker={labels.worker}}}", n)


def items_persisted_total(labels: MetricLabels, n: int) -> None:
    metrics.incr(f"items_persisted_total{{worker={labels.worker}}}", n)


def items_skipped_total(labels: MetricLabels, n: int) -> None:
    metrics.incr(f"items_skipped_total{{worker={labels.worker}}}", n)


def errors_total(labels: MetricLabels, stage: str, n: int = 1) -> None:
    metrics.incr(f"errors_total{{worker={labels.worker},stage={stage}}}", n)


def as_dict() -> dict[str, Any]:
    return {"counters": dict(metrics.counters), "timings": dict(metrics.timings)}
