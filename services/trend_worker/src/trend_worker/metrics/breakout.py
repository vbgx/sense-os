from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class DailyCount:
    day: date
    count: float


History = Iterable[DailyCount]


def compute_breakout_score(history: History) -> float:
    pts = list(history)
    if len(pts) < 14:
        return 0.0

    xs = [float(p.count) for p in pts]
    last7 = xs[-7:]
    prev7 = xs[-14:-7]

    a = sum(last7) / 7.0
    b = sum(prev7) / 7.0

    if b <= 0:
        return 0.0

    ratio = a / b
    score = (ratio - 1.0) * 100.0
    if score < 0:
        score = 0.0
    if score > 100.0:
        score = 100.0
    return float(score)


def compute(history: History) -> float:
    return compute_breakout_score(history)
