from processing_worker.features.pain_score import compute_pain_score


def test_pain_score_basic():
    features = {"question": 1.0, "frustration": 0.8}
    score, breakdown = compute_pain_score(features)
    assert isinstance(score, float)
    assert isinstance(breakdown, dict)
