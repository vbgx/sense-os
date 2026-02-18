from __future__ import annotations

from trend_worker.metrics.types import History


def compute(history: History) -> float:
    xs = [p.count for p in history]
    if len(xs) < 14:
        return 0.0

    prev = sum(xs[-14:-7]) / 7.0
    last = sum(xs[-7:]) / 7.0
    if prev <= 0:
        return 0.0
    drop = (prev - last) / prev
    return float(max(0.0, drop))
