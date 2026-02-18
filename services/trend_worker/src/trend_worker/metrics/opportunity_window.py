from __future__ import annotations

from trend_worker.metrics.types import History


def compute(history: History) -> float:
    xs = [p.count for p in history]
    if len(xs) < 21:
        return 0.0

    early = sum(xs[-21:-14]) / 7.0
    mid = sum(xs[-14:-7]) / 7.0
    late = sum(xs[-7:]) / 7.0

    if early <= 0:
        return 0.0

    growth1 = (mid - early) / early
    growth2 = (late - mid) / mid if mid > 0 else 0.0

    if growth1 <= 0:
        return 0.0

    if growth2 < 0:
        return float(min(1.0, growth1))

    return float(min(1.0, (growth1 + growth2) / 2.0))
