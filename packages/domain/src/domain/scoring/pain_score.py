from dataclasses import asdict
from domain.models.pain_features import FeatureVector


def score(features: FeatureVector) -> tuple[float, dict]:
    score = 0.0
    if features.is_question:
        score += 1.5
    score += min(2.0, 0.6 * features.pain_hits)
    score += min(1.0, 0.7 * features.workaround_hits)
    score += min(0.8, 0.4 * features.money_hits)
    if features.length < 80:
        score -= 0.7
    score += features.sentiment
    score = max(0.0, min(5.0, score))
    breakdown = {"algo": "heuristics_v1", "score": round(score, 2), **asdict(features)}
    return score, breakdown
