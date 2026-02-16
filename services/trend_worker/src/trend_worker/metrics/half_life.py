from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class DailyHalfLifePoint:
    """
    Minimal daily series for half-life estimation.

    day: YYYY-MM-DD
    count: daily signal volume for the cluster
    """
    day: str
    count: int


def _safe_log(x: float) -> float:
    return math.log(max(1e-12, x))


def _median(xs: list[float]) -> float:
    if not xs:
        return 0.0
    xs2 = sorted(xs)
    n = len(xs2)
    mid = n // 2
    if n % 2 == 1:
        return xs2[mid]
    return 0.5 * (xs2[mid - 1] + xs2[mid])


def estimate_half_life_days(
    daily: Iterable[DailyHalfLifePoint],
    *,
    window_decay: int = 21,
    min_days: int = 28,
    peak_search_days: int = 60,
    min_peak_count: int = 10,
) -> Optional[float]:
    """
    Estimate trend half-life in days: time for activity to drop by half.

    Heuristic (deterministic, stable):
    1) Sort daily by day
    2) Identify peak within last peak_search_days
    3) Look at post-peak segment
    4) Estimate daily decay slope in log-space:
         slope ≈ median( log(c_t+1) - log(c_{t-1}+1) ) over a decay window
       (median makes it robust to spikes)
    5) If slope is negative, interpret exponential decay:
         c(t) ≈ c0 * exp(slope * t)
       Half-life = ln(2) / (-slope)
    6) Return None if:
       - insufficient data
       - no meaningful peak
       - slope >= 0 (not decaying)

    Notes:
    - This is not forecasting. It's a descriptive metric from historical decay.
    - Uses log1p so zeros do not break.
    """
    items = list(daily)
    if not items:
        return None

    items.sort(key=lambda d: d.day)
    counts = [max(0, int(p.count)) for p in items]

    if len(counts) < min_days:
        return None

    # Search peak in last peak_search_days
    start_idx = max(0, len(counts) - peak_search_days)
    sub = counts[start_idx:]
    peak_rel = max(range(len(sub)), key=lambda i: sub[i])
    peak_idx = start_idx + peak_rel
    peak_val = counts[peak_idx]

    if peak_val < min_peak_count:
        return None

    # Post-peak data
    post = counts[peak_idx:]
    if len(post) < 7:
        return None

    # Use at most window_decay days after peak
    post = post[:window_decay]
    if len(post) < 7:
        return None

    # Compute log-deltas
    deltas: list[float] = []
    prev = math.log1p(post[0])
    for c in post[1:]:
        cur = math.log1p(c)
        deltas.append(cur - prev)
        prev = cur

    slope = _median(deltas)  # robust daily log-change
    if slope >= -1e-6:
        # Not decaying (flat or growing) => half-life undefined/infinite
        return None

    half_life = math.log(2.0) / (-slope)

    # Cap to a sane range for stability (avoid absurd values on near-flat decay)
    if half_life < 0:
        return None
    if half_life > 3650:
        half_life = 3650.0

    return float(round(half_life, 2))
