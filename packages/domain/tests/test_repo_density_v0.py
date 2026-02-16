from pathlib import Path
from domain.competition.repo_density_v0 import compute_repo_density_score_v0


FIXTURE = Path("tools/fixtures/competition/github_repos_snapshot_v0.jsonl")


def test_high_density_returns_refunds_reconciliation():
    summary = "Refund reconciliation for ecommerce payouts is painful"
    key_phrases = ["refunds", "reconciliation", "payouts", "ecommerce"]
    result = compute_repo_density_score_v0(summary, key_phrases, FIXTURE)
    assert result.repo_density_score >= 35
    assert result.matching_repo_count >= 1


def test_low_density_niche_pain():
    summary = "Underwater acoustic calibration for Arctic sensors is difficult"
    key_phrases = ["acoustic calibration", "arctic sensors"]
    result = compute_repo_density_score_v0(summary, key_phrases, FIXTURE)
    assert result.repo_density_score <= 15


def test_stable_between_runs():
    summary = "Shopify returns portal is needed"
    key_phrases = ["shopify", "returns", "portal"]
    r1 = compute_repo_density_score_v0(summary, key_phrases, FIXTURE)
    r2 = compute_repo_density_score_v0(summary, key_phrases, FIXTURE)
    assert r1.repo_density_score == r2.repo_density_score
    assert r1.matching_repo_count == r2.matching_repo_count
    assert r1.weighted_stars == r2.weighted_stars
