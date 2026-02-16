from pathlib import Path
from domain.competition.ph_overlap_v0 import compute_ph_overlap_score_v0


FIXTURE = Path("tools/fixtures/competition/producthunt_snapshot_v0.jsonl")


def test_high_overlap_returns_shopify():
    summary = "Shopify returns and refunds are chaotic; we need an automated reconciliation layer for return-heavy stores"
    result = compute_ph_overlap_score_v0(summary, FIXTURE)
    assert result.ph_overlap_score >= 40
    assert result.similar_launch_count >= 3


def test_low_overlap_niche_pain():
    summary = "Hard to manage acoustic calibration for underwater sensors in Arctic conditions"
    result = compute_ph_overlap_score_v0(summary, FIXTURE)
    assert result.ph_overlap_score <= 15


def test_stable_between_runs():
    summary = "Refund reconciliation for ecommerce payouts is painful"
    r1 = compute_ph_overlap_score_v0(summary, FIXTURE)
    r2 = compute_ph_overlap_score_v0(summary, FIXTURE)
    assert r1.ph_overlap_score == r2.ph_overlap_score
    assert r1.similar_launch_count == r2.similar_launch_count
    assert r1.max_similarity == r2.max_similarity
