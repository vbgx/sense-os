from __future__ import annotations

from math import sqrt

from trend_worker.metrics.types import History


def compute(history: History) -> float:
    xs = [p.count for p in history]
    if len(xs) < 7:
        return 0.0

    window = xs[-7:]
    mean = sum(window) / len(window)
    var = sum((x - mean) ** 2 for x in window) / len(window)
    std = sqrt(var) if var > 0 else 0.0
    if mean <= 0:
        return float(std)
    return float(std / mean)
