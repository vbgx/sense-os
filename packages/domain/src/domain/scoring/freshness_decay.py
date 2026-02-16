from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def compute_freshness_weight(
    *,
    created_at: Optional[datetime],
    lambda_per_day: float,
    now: Optional[datetime] = None,
) -> float:
    if created_at is None:
        return 0.5

    if now is None:
        now = _now_utc()

    created_at_utc = _as_utc(created_at)
    now_utc = _as_utc(now)

    age_days = (now_utc - created_at_utc).total_seconds() / 86400.0
    if age_days < 0.0:
        age_days = 0.0

    w = math.exp(-float(lambda_per_day) * float(age_days))
    if w < 0.0:
        return 0.0
    if w > 1.0:
        return 1.0
    return float(w)


def apply_freshness_to_score(
    *,
    score_0_100: float,
    freshness_weight_0_1: float,
    floor: float = 0.40,
) -> float:
    w = max(0.0, min(1.0, float(freshness_weight_0_1)))
    f = max(0.0, min(1.0, float(floor)))
    mult = f + (1.0 - f) * w
    out = float(score_0_100) * mult
    if out < 0.0:
        return 0.0
    if out > 100.0:
        return 100.0
    return out
