from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class FeatureMetrics:
    timings_ms: dict[str, list[float]]
    errors: dict[str, int]
    nulls: dict[str, int]

    def __init__(self) -> None:
        self.timings_ms = {}
        self.errors = {}
        self.nulls = {}

    def record_timing(self, name: str, ms: float) -> None:
        self.timings_ms.setdefault(name, []).append(ms)

    def record_error(self, name: str) -> None:
        self.errors[name] = self.errors.get(name, 0) + 1

    def record_null(self, name: str) -> None:
        self.nulls[name] = self.nulls.get(name, 0) + 1


def timed_call(metrics: FeatureMetrics, feature_name: str, fn, **kwargs) -> Any:
    start = time.perf_counter()
    try:
        out = fn(**kwargs)
    except Exception:
        metrics.record_error(feature_name)
        raise
    finally:
        ms = (time.perf_counter() - start) * 1000.0
        metrics.record_timing(feature_name, ms)

    if out is None:
        metrics.record_null(feature_name)

    return out
