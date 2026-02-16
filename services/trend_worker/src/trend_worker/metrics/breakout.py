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

    # Moving average
    ma = []
    for i in range(len(counts)):
        start = max(0, i - window_ma + 1)
        w = counts[start : i + 1]
        ma.append(sum(w) / float(len(w)))

    y = [math.log1p(v) for v in ma]

    # Need at least 3 points for acceleration
    if len(y) < 3:
        return 0

    acc = []
    for i in range(2, len(y)):
        a = y[i] - 2.0 * y[i - 1] + y[i - 2]
        acc.append(a)

    if len(acc) < 5:
        return 0

    a_last = acc[-1]

    # Baseline window excludes the last 2 acceleration points to avoid leakage
    # (we want historical baseline)
    baseline = acc[:-2]
    if not baseline:
        return 0

    # Take last baseline_days from baseline (if available)
    baseline = baseline[-baseline_days:]

    mu = _mean(baseline)
    sigma = _std(baseline)

    if sigma <= 1e-6:
        # Baseline is flat; treat as no evidence of anomalous acceleration
        # unless the last accel is substantially positive.
        # Map small positive accel to small score, large accel to moderate.
        z = 10.0 if a_last > 0.25 else (3.0 if a_last > 0.10 else (1.0 if a_last > 0.03 else 0.0))
    else:
        z = (a_last - mu) / sigma

    # Require being above baseline meaningfully; shift left to make small z low.
    z_adj = z - 1.5
    ratio = _sigmoid01(z_adj)
    ratio = _clamp01(ratio)

    return int(round(100.0 * ratio))
