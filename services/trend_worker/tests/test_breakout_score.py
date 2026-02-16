from __future__ import annotations

from trend_worker.metrics.breakout import DailyCount, compute_breakout_score


def _mk(days: int, fn):
    out = []
    for i in range(days):
        out.append(DailyCount(day=f"2026-01-{i+1:02d}", count=int(fn(i))))
    return out


def test_breakout_linear_growth_is_low():
    # steady linear increase: no sudden acceleration anomaly
    daily = _mk(40, lambda i: 10 + i)  # 10,11,12...
    s = compute_breakout_score(daily)
    assert s <= 40


def test_breakout_sudden_acceleration_is_high():
    # flat then sudden ramp
    def f(i: int) -> int:
        if i < 25:
            return 10
        if i < 30:
            return 10 + (i - 25) * 8   # ramp
        return 50 + (i - 30) * 12      # accelerating

    daily = _mk(45, f)
    s = compute_breakout_score(daily)
    assert s >= 60


def test_breakout_requires_min_days():
    daily = _mk(10, lambda i: 10 + i)
    assert compute_breakout_score(daily) == 0


def test_breakout_bounded_0_100():
    daily = _mk(80, lambda i: 1 if i < 60 else 2000 + (i - 60) * 3000)
    s = compute_breakout_score(daily)
    assert 0 <= s <= 100
