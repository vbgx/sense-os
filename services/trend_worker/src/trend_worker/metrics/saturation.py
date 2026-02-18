from __future__ import annotations

from trend_worker.metrics.types import History


def compute(history: History) -> float:
    xs = [p.count for p in history]
    if len(xs) < 21:
        return 0.0

    a = sum(xs[-21:-14]) / 7.0
    b = sum(xs[-14:-7]) / 7.0
    c = sum(xs[-7:]) / 7.0

    if a <= 0:
        return 0.0

    g1 = (b - a) / a
    g2 = (c - b) / b if b > 0 else 0.0

    if g1 > 0 and g2 <= 0:
        return float(min(1.0, abs(g2)))

    if g1 > 0 and g2 > 0 and g2 < (g1 * 0.25):
        return float(min(1.0, (g1 - g2) / max(1e-9, g1)))

    return 0.0
