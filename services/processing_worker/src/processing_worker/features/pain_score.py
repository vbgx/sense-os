from __future__ import annotations

from typing import Any

from domain.scoring.pain_score import compute as _compute_domain_pain_score


def compute_pain_score(
    content: str,
    *,
    language_code: str | None = None,
    features: dict[str, Any] | None = None,
) -> float:
    feat = dict(features or {})
    feat.setdefault("text", content)
    if language_code is not None:
        feat.setdefault("language_code", language_code)
    return float(_compute_domain_pain_score(features=feat))
