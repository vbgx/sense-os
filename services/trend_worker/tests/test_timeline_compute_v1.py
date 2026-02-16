from __future__ import annotations

from datetime import date

from trend_worker.timeline import DailyVolume, compute_timeline


def test_timeline_is_stable_and_consistent():
    vols = [
        DailyVolume(date(2026, 1, 1), 2),
        DailyVolume(date(2026, 1, 2), 3),
        DailyVolume(date(2026, 1, 3), 10),
        DailyVolume(date(2026, 1, 4), 16),
    ]
    t1 = compute_timeline(vols)
    t2 = compute_timeline(vols)

    assert t1 == t2
    assert len(t1) == 4

    # day 1 baseline
    assert t1[0].growth_rate == 0.0
    assert t1[0].velocity == 0.0
    assert t1[0].breakout_flag is False

    # day 2: +1 on 2 => 0.5 growth
    assert t1[1].velocity == 1.0
    assert abs(t1[1].growth_rate - 0.5) < 1e-9

    # breakout heuristic v1: velocity>=5, growth>=0.5, volume>=10
    # day 3: 10-3=7 vel, growth=7/3=2.333, volume=10 => breakout true
    assert t1[2].breakout_flag is True
