from __future__ import annotations

from trend_worker.metrics.types import History


def compute(history: History) -> float:
    xs = [p.count for p in history]
    if not xs:
        return 0.0
    return float(xs[-1])
