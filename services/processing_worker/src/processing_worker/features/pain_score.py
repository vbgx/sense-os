from __future__ import annotations

from typing import Any

from domain.scoring.pain_score import compute as _compute_domain_pain_score


def compute_pain_score(text: str, *, features: dict[str, Any] | None = None) -> tuple[float, dict[str, Any]]:
    feat = dict(features or {})
    feat.setdefault("text", text)
    score = float(_compute_domain_pain_score(features=feat))
    return score, {"pain_score": score}
