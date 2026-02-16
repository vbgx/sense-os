from __future__ import annotations

import math

from trend_worker.metrics.half_life import DailyHalfLifePoint, estimate_half_life_days


def _mk(days: int, fn):
    out = []
    for i in range(days):
        out.append(DailyHalfLifePoint(day=f"2026-01-{i+1:02d}", count=int(fn(i))))
    return out


def test_half_life_short_for_fast_decay():
    # peak then exponential decay with half-life ~5 days
    hl_true = 5.0
    k = math.log(2.0) / hl_true  # decay constant
    def f(i: int) -> float:
        if i < 20:
            return 10 + i  # ramp
        t = i - 20
        return 200.0 * math.exp(-k * t)

    daily = _mk(60, f)
    hl = estimate_half_life_days(daily)
    assert hl is not None
    assert hl <= 12


def test_half_life_long_for_slow_decay():
    # peak then slow decay with half-life ~60 days
    hl_true = 60.0
    k = math.log(2.0) / hl_true
    def f(i: int) -> float:
        if i < 25:
            return 10 + i * 3
        t = i - 25
        return 300.0 * math.exp(-k * t)

    daily = _mk(120, f)
    hl = estimate_half_life_days(daily)
    assert hl is not None
    assert hl >= 20


def test_half_life_none_when_not_decaying():
    daily = _mk(60, lambda i: 50 + i)  # still growing
    assert estimate_half_life_days(daily) is None


def test_half_life_stable_on_identical_run():
    daily = _mk(90, lambda i: 200 if i < 30 else max(1, 200 - (i - 30) * 3))
    hl1 = estimate_half_life_days(daily)
    hl2 = estimate_half_life_days(daily)
    assert hl1 == hl2
