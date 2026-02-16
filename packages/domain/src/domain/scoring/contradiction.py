from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional


@dataclass(frozen=True)
class ContradictionSignal:
    """
    Minimal signal view for contradiction detection.

    sentiment_compound expected in [-1..+1] (negative=negative).
    created_at used for volatility heuristics (optional).
    """
    sentiment_compound: Optional[float] = None
    created_at: Optional[datetime] = None


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _variance(vals: list[float]) -> float:
    if len(vals) <= 1:
        return 0.0
    m = sum(vals) / float(len(vals))
    return sum((v - m) ** 2 for v in vals) / float(len(vals))


def _temporal_volatility(signals: list[ContradictionSignal]) -> float:
    """
    Returns [0..1] measuring abnormal day-to-day sentiment volatility.
    Heuristic:
      - bucket by UTC day
      - compute daily mean sentiment
      - compute mean absolute delta between consecutive days
      - normalize by max possible delta (2.0) then clamp
    """
    buckets: dict[str, list[float]] = {}
    for s in signals:
        if s.created_at is None or s.sentiment_compound is None:
            continue
        dt = s.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        key = dt.strftime("%Y-%m-%d")
        buckets.setdefault(key, []).append(float(s.sentiment_compound))

    if len(buckets) < 2:
        return 0.0

    days = sorted(buckets.keys())
    daily_means = []
    for d in days:
        vals = buckets[d]
        daily_means.append(sum(vals) / float(len(vals)))

    deltas = []
    for i in range(1, len(daily_means)):
        deltas.append(abs(daily_means[i] - daily_means[i - 1]))

    if not deltas:
        return 0.0

    mean_delta = sum(deltas) / float(len(deltas))
    # sentiment range is [-1..+1], max delta between days is 2.0
    return _clamp01(mean_delta / 2.0)


def compute_contradiction_index(
    signals: Iterable[ContradictionSignal],
    *,
    w_variance: float = 0.55,
    w_polarization: float = 0.30,
    w_volatility: float = 0.15,
    neutral_band: float = 0.10,
) -> int:
    """
    Contradiction Index (0..100), cluster-level.

    Components:
    - sentiment variance (higher variance => more contradictory)
    - polarization (balanced ratio of positive vs negative => higher contradiction)
    - temporal volatility (day-to-day sentiment swings)

    Notes:
    - This is not semantic contradiction NLP. Pure numeric heuristics.
    - Deterministic & bounded.
    """
    items = list(signals)
    vals = [float(s.sentiment_compound) for s in items if s.sentiment_compound is not None]
    if len(vals) == 0:
        return 0

    # Variance: sentiment variance is bounded by ~1.0 for [-1..1].
    var = _variance(vals)
    var_norm = _clamp01(var / 1.0)

    # Polarization: reward near 50/50 pos/neg; penalize overwhelmingly one-sided.
    pos = 0
    neg = 0
    for v in vals:
        if v >= neutral_band:
            pos += 1
        elif v <= -neutral_band:
            neg += 1
    total_pn = pos + neg
    if total_pn == 0:
        pol = 0.0
    else:
        ratio = pos / float(total_pn)
        # distance to 0.5 (balanced). 0 at extremes, 1 at perfect balance.
        pol = 1.0 - (abs(ratio - 0.5) / 0.5)
        pol = _clamp01(pol)

    # Temporal volatility (optional)
    vol = _temporal_volatility(items)

    ratio = (w_variance * var_norm) + (w_polarization * pol) + (w_volatility * vol)
    ratio = _clamp01(ratio)
    return int(round(100.0 * ratio))
