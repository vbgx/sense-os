from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class DailyHalfLifePoint:
    day: date
    count: float


History = Iterable[DailyHalfLifePoint]


def estimate_half_life_days(history: History) -> float | None:
    pts = list(history)
    if len(pts) < 10:
        return None

    xs = [float(p.count) for p in pts]
    peak = max(xs)
    if peak <= 0:
        return None

    last = xs[-1]
    if last >= peak * 0.7:
        return None

    target = peak / 2.0
    peak_i = xs.index(peak)

    for i in range(peak_i, len(xs)):
        if xs[i] <= target:
            return float(i - peak_i)

    return None


def compute(history: History) -> float:
    v = estimate_half_life_days(history)
    return 0.0 if v is None else float(v)
