from __future__ import annotations

from domain.scoring.opportunity_window import OpportunityInputs, OpportunityWindowStatus, compute_opportunity_window


def test_early_breakout_high_saturation_low_is_early():
    r = compute_opportunity_window(
        OpportunityInputs(breakout_score=80, saturation_score=20, growth_momentum=70, half_life_days=30)
    )
    assert r.opportunity_window_status == OpportunityWindowStatus.EARLY
    assert 0 <= r.opportunity_window_score <= 100


def test_saturating_breakout_low_saturation_high_is_saturating():
    r = compute_opportunity_window(
        OpportunityInputs(breakout_score=25, saturation_score=80, growth_momentum=20, half_life_days=10)
    )
    assert r.opportunity_window_status == OpportunityWindowStatus.SATURATING
    assert 0 <= r.opportunity_window_score <= 100


def test_peak_midrange_is_peak():
    r = compute_opportunity_window(
        OpportunityInputs(breakout_score=55, saturation_score=45, growth_momentum=55, half_life_days=40)
    )
    assert r.opportunity_window_status == OpportunityWindowStatus.PEAK
    assert 0 <= r.opportunity_window_score <= 100


def test_score_bounded():
    r = compute_opportunity_window(
        OpportunityInputs(breakout_score=999, saturation_score=-10, growth_momentum=500, half_life_days=-1)
    )
    assert 0 <= r.opportunity_window_score <= 100
