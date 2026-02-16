from pathlib import Path
from domain.competition.keyword_saturation_v0 import compute_keyword_saturation_score_v0


FIXTURE = Path("tools/fixtures/competition/keyword_index_snapshot_v0.json")


def test_generic_keywords_high_score():
    key_phrases = ["Shopify returns refund policy", "support workflow automation"]
    result = compute_keyword_saturation_score_v0(key_phrases, FIXTURE)
    assert result.keyword_saturation_score >= 50
    assert "shopify" in result.matched_terms


def test_niche_keywords_low_score():
    key_phrases = ["underwater acoustic calibration", "thermocline spectral drift"]
    result = compute_keyword_saturation_score_v0(key_phrases, FIXTURE)
    assert result.keyword_saturation_score <= 25


def test_stable_between_runs():
    key_phrases = ["refund reconciliation payouts"]
    r1 = compute_keyword_saturation_score_v0(key_phrases, FIXTURE)
    r2 = compute_keyword_saturation_score_v0(key_phrases, FIXTURE)
    assert r1.keyword_saturation_score == r2.keyword_saturation_score
    assert r1.matched_terms == r2.matched_terms
    assert r1.avg_frequency == r2.avg_frequency
