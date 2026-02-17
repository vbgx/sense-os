from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence, Optional


@dataclass(frozen=True)
class DailySaturationPoint:
    """
    Minimal daily series for saturation detection.

    - day: YYYY-MM-DD
    - count: daily signal volume for the cluster
    - unique_users: optional daily unique user count (if available)
    """
    day: str
    count: int
    unique_users: Optional[int] = None


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


def _moving_average(counts: list[float], window: int) -> list[float]:
    out: list[float] = []
    for i in range(len(counts)):
        start = max(0, i - window + 1)
        w = counts[start : i + 1]
        out.append(sum(w) / float(len(w)))
    return out


def _slope(xs: Sequence[float]) -> float:
    """
    Simple linear slope via endpoints (stable, cheap).
    xs must have len>=2.
    """
    if len(xs) < 2:
        return 0.0
    return (xs[-1] - xs[0]) / float(len(xs) - 1)


def compute_saturation_score(
    daily: Iterable[DailySaturationPoint],
    *,
    window_ma: int = 7,
    min_days: int = 21,
    recent_days: int = 14,
    plateau_epsilon_ratio: float = 0.08,
    max_decline_for_saturation: float = -0.10,
) -> int:
    """
    Saturation Score (0..100): detects plateau / deceleration after a peak.

    Heuristics (cluster-level):
    - Flattening curve in recent period (low slope)
    - Deceleration vs earlier trend (slope drop)
    - Plateau stability (low variance in recent)
    - Optional: decreasing new-user ratio (unique_users/count) in recent window

    Distinction vs "declining":
    - Saturation is primarily plateau/flattening.
    - Strong negative slope (prolonged decline) reduces saturation score.

    Definition-of-done intent:
    - Stable plateau after peak => high saturation
    - Active growth => low saturation
    - Strong decline => not treated as saturation (separate "declining" metric)
    """
    items = list(daily)
    if not items:
        return 0

    items.sort(key=lambda d: d.day)
    counts = [float(max(0, int(p.count))) for p in items]

    if len(counts) < min_days:
        return 0

    # Smooth & stabilize (log-space reduces huge-count dominance)
    ma = _moving_average(counts, window_ma)
    y = [math.log1p(v) for v in ma]

    # Split periods
    recent = y[-recent_days:]
    prev = y[-2 * recent_days : -recent_days] if len(y) >= 2 * recent_days else y[:-recent_days]

    if len(recent) < 5 or len(prev) < 5:
        return 0

    # Peak check: if no clear peak before recent window, saturation is unlikely
    peak = max(y)
    recent_max = max(recent)
    peak_before_recent = max(y[:-recent_days]) if len(y) > recent_days else peak
    has_peak_before_recent = peak_before_recent >= recent_max * 1.02  # small margin

    # Slopes (endpoint slope)
    slope_recent = _slope(recent)
    slope_prev = _slope(prev)

    # Flattening: slope near 0 => high
    # Convert to 0..1 by comparing absolute slope to epsilon
    # epsilon scales with magnitude of series; use recent mean as baseline
    recent_mean = _mean(recent)
    eps = max(1e-6, plateau_epsilon_ratio * max(0.5, abs(recent_mean)))
    flatness = _clamp01(1.0 - (abs(slope_recent) / eps))

    # Deceleration: if slope dropped significantly vs previous => high
    # We care about "growth slowing", so compare slope_prev - slope_recent (positive => decel)
    decel_raw = slope_prev - slope_recent
    # Normalize decel by eps
    decel = _clamp01(decel_raw / (2.0 * eps))

    # Plateau stability: low std in recent => high
    st = _std(recent)
    stability = _clamp01(1.0 - (st / (3.0 * eps)))

    # Optional "new user ratio" drop (if unique_users available)
    # Proxy: mean(unique_users/count) in prev vs recent; drop => more saturation
    ratio_component = 0.0
    if all(p.unique_users is not None for p in items[-recent_days:]) and all(
        p.unique_users is not None for p in items[-2 * recent_days : -recent_days]
    ):
        def _mean_ratio(points: list[DailySaturationPoint]) -> float:
            rs = []
            for q in points:
                c = max(1, int(q.count))
                u = max(0, int(q.unique_users or 0))
                rs.append(min(1.0, u / float(c)))
            return _mean(rs)

        prev_points = items[-2 * recent_days : -recent_days]
        recent_points = items[-recent_days:]
        r_prev = _mean_ratio(prev_points)
        r_recent = _mean_ratio(recent_points)
        drop = _clamp01((r_prev - r_recent) / max(1e-6, r_prev))
        ratio_component = drop

    # Decline penalty: strong negative slope means "declining" not "saturation"
    # If slope_recent is below max_decline_for_saturation, reduce score.
    decline_penalty = 1.0
    if slope_recent < max_decline_for_saturation:
        # map deeper declines to stronger penalty
        # slope_recent is in log space; treat below threshold as penalized
        severity = _clamp01((abs(slope_recent) - abs(max_decline_for_saturation)) / (3.0 * abs(max_decline_for_saturation)))
        decline_penalty = _clamp01(1.0 - 0.8 * severity)

    # Peak gating: saturation should be more plausible if we already peaked
    peak_gate = 1.0 if has_peak_before_recent else 0.75

    # Combine
    # Flatness is the core signal; decel & stability reinforce.
    ratio = (
        0.45 * flatness
        + 0.30 * decel
        + 0.20 * stability
        + 0.05 * ratio_component
    )
    ratio = _clamp01(ratio * decline_penalty * peak_gate)

    return int(round(100.0 * ratio))
