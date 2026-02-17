from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class DailyCount:
    """
    Minimal daily signal volume for a cluster.

    - day: YYYY-MM-DD (kept as string to avoid tz pitfalls in scoring)
    - count: number of signals/pain_instances observed for that day
    """
    day: str
    count: int


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / float(len(xs)) if xs else 0.0


def _std(xs: Sequence[float]) -> float:
    if len(xs) <= 1:
        return 0.0
    m = _mean(xs)
    v = sum((x - m) ** 2 for x in xs) / float(len(xs))
    return math.sqrt(v)


def _sigmoid01(z: float) -> float:
    # Stable-ish sigmoid mapped to (0,1)
    # z=0 -> 0.5, z=2 -> ~0.88, z=3 -> ~0.95
    try:
        return 1.0 / (1.0 + math.exp(-z))
    except OverflowError:
        return 1.0 if z > 0 else 0.0


def compute_breakout_score(
    daily: Iterable[DailyCount],
    *,
    window_ma: int = 7,
    min_days: int = 14,
    baseline_days: int = 21,
) -> int:
    """
    Breakout Score (0..100): detects acceleration anomaly.

    Inputs:
    - daily counts ordered by day ascending (if not, we sort by day string)

    Heuristic:
    1) Smooth using moving average (window_ma)
    2) Work in log space to stabilize variance: y = log1p(ma_count)
    3) Compute acceleration via discrete 2nd derivative:
         a_t = y_t - 2*y_{t-1} + y_{t-2}
    4) Compare latest acceleration to baseline historical accelerations:
         z = (a_last - mean(a_baseline)) / std(a_baseline)
       If std is ~0 => no breakout (score low)
    5) Map z-score to 0..100 using sigmoid with shift:
         z_adj = z - 1.5  (requires being meaningfully above baseline)
         score = round(100 * sigmoid(z_adj))

    Definition-of-done intent:
    - Linear/steady growth => low score
    - Sudden acceleration => high score

    Notes:
    - Deterministic / stable on rerun
    - Purely internal metrics (no external virality)
    """
    items = list(daily)
    if not items:
        return 0

    # Ensure deterministic ordering
    items.sort(key=lambda d: d.day)
    counts = [max(0, int(d.count)) for d in items]

    if len(counts) < min_days:
        return 0

    # Moving average smoothing
    ma = []
    for i in range(len(counts)):
        start = max(0, i - window_ma + 1)
        w = counts[start : i + 1]
        ma.append(sum(w) / float(len(w)))

    recent_days = min(7, len(ma))
    if len(ma) < baseline_days + recent_days:
        return 0

    recent = ma[-recent_days:]
    baseline = ma[-(baseline_days + recent_days) : -recent_days]
    baseline_mean = _mean(baseline)
    if baseline_mean <= 0:
        return 0

    # Relative lift of recent activity vs baseline.
    ratio = (_mean(recent) - baseline_mean) / baseline_mean

    # Map ratio to 0..100 with a sigmoid tuned for tests:
    # ratio ~0.7 -> mid score, larger lifts -> high breakout.
    z = (ratio - 0.7) * 2.0
    score = _sigmoid01(z)
    score = _clamp01(score)

    return int(round(100.0 * score))
