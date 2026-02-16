from __future__ import annotations

from datetime import datetime, timezone, timedelta

from domain.scoring.signal_quality import compute_signal_quality_score


def test_short_low_info_post_scores_low():
    s = "help??"
    score = compute_signal_quality_score(content=s, created_at=datetime.now(tz=timezone.utc))
    assert score <= 25


def test_detailed_case_study_scores_high():
    s = """
    I built a B2B SaaS and hit $12k MRR in 6 months.
    Churn was 6% monthly. We reduced it to 3% by fixing onboarding.
    CAC is ~$120 and LTV is ~$2400. Pricing tests improved conversion by 18%.
    Here's the exact process and workflow we used.
    """
    score = compute_signal_quality_score(content=s, created_at=datetime.now(tz=timezone.utc))
    assert score >= 65


def test_freshness_penalizes_old_content():
    s = "I built a SaaS with $5k MRR and here is the full breakdown and numbers."
    fresh = compute_signal_quality_score(content=s, created_at=datetime.now(tz=timezone.utc))
    old = compute_signal_quality_score(content=s, created_at=datetime.now(tz=timezone.utc) - timedelta(days=120))
    assert old < fresh
