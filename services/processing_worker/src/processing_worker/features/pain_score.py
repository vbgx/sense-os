from processing_worker.features.markers import features


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def score_text(text: str) -> tuple[float, dict]:
    f = features(text)

    score = 0.0

    # Question = intent
    if f["is_question"]:
        score += 1.5

    # Pain language
    score += min(2.0, 0.6 * f["pain_hits"])

    # Workarounds signal real pain
    score += min(1.0, 0.7 * f["workaround_hits"])

    # Money signal (willingness)
    score += min(0.8, 0.4 * f["money_hits"])

    # Too short -> penalize
    if f["len"] < 80:
        score -= 0.7

    score = clamp(score, 0.0, 5.0)

    breakdown = {
        "algo": "heuristics_v1",
        "score": round(score, 2),
        **f,
    }
    return score, breakdown

# Backward-compatible API expected by tests

def compute_pain_score(feature_map: dict | str) -> tuple[float, dict]:
    if isinstance(feature_map, dict):
        question = float(feature_map.get("question", 0.0))
        frustration = float(feature_map.get("frustration", 0.0))
        score = clamp(2.5 * question + 2.5 * frustration, 0.0, 5.0)
        breakdown = {
            "algo": "features_v1",
            "score": round(score, 2),
            **feature_map,
        }
        return score, breakdown
    return score_text(feature_map)
