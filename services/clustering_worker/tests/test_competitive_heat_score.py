from __future__ import annotations

from domain.scoring.competitive_heat import CompetitiveHeatSignal, compute_competitive_heat_score


def test_heat_low_when_no_solution_mentions():
    signals = [
        CompetitiveHeatSignal(text="This is painful and confusing. Nothing works."),
        CompetitiveHeatSignal(text="We are stuck and need a fix."),
    ]
    s = compute_competitive_heat_score(signals)
    assert s <= 35


def test_heat_high_when_alternatives_mentioned():
    signals = [
        CompetitiveHeatSignal(text="Already solved by X, we switched to Y."),
        CompetitiveHeatSignal(text="Instead of building this, just use a tool out of the box."),
        CompetitiveHeatSignal(text="We migrated to another platform; this feature already exists."),
    ]
    s = compute_competitive_heat_score(signals)
    assert s >= 50


def test_heat_bounded_0_100():
    signals = [CompetitiveHeatSignal(text=("already solved by we switched to " * 500)) for _ in range(100)]
    s = compute_competitive_heat_score(signals)
    assert 0 <= s <= 100
