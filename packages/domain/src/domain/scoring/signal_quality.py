from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_MONEY_RE = re.compile(r"(\$|€|mrr|arr|revenue|pricing|churn|cac|ltv|conversion|pipeline)", re.IGNORECASE)
_CONTEXT_RE = re.compile(r"\b(i built|we built|my startup|our product|customers|users|client|b2b|saas|ops|workflow|process)\b", re.IGNORECASE)
_SPECIFICITY_RE = re.compile(r"\b(\d{1,3}%|\d{2,6}\s?(users|customers|leads|days|weeks|months)|mrr|arr)\b", re.IGNORECASE)


@dataclass(frozen=True)
class SignalQualityComponents:
    length: float
    specificity: float
    business_context: float
    link_density: float
    freshness: float
    engagement: float


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def _freshness_score(created_at: Optional[datetime], *, half_life_days: float = 21.0) -> float:
    if created_at is None:
        return 0.5
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (_now_utc() - created_at).total_seconds() / 86400.0
    age_days = max(age_days, 0.0)
    import math
    return float(math.exp(-age_days / float(half_life_days)))


def compute_signal_quality_components(
    *,
    content: str,
    created_at: Optional[datetime] = None,
    engagement_norm01: Optional[float] = None,
) -> SignalQualityComponents:
    text = content or ""
    n = len(text)

    length = _clamp01(n / 1200.0)

    specificity = 1.0 if _SPECIFICITY_RE.search(text) else 0.0
    business_context = 0.0
    if _MONEY_RE.search(text):
        business_context += 0.5
    if _CONTEXT_RE.search(text):
        business_context += 0.5
    business_context = _clamp01(business_context)

    urls = len(_URL_RE.findall(text))
    link_density = _clamp01(urls / 3.0)

    freshness = _clamp01(_freshness_score(created_at))

    engagement = _clamp01(engagement_norm01 if engagement_norm01 is not None else 0.0)

    return SignalQualityComponents(
        length=length,
        specificity=specificity,
        business_context=business_context,
        link_density=link_density,
        freshness=freshness,
        engagement=engagement,
    )


def compute_signal_quality_score(
    *,
    content: str,
    created_at: Optional[datetime] = None,
    engagement_norm01: Optional[float] = None,
) -> int:
    c = compute_signal_quality_components(
        content=content,
        created_at=created_at,
        engagement_norm01=engagement_norm01,
    )

    score01 = (
        0.35 * c.length
        + 0.20 * c.specificity
        + 0.25 * c.business_context
        + 0.05 * c.link_density
        + 0.15 * c.freshness
        + 0.00 * c.engagement
    )

    score01 = _clamp01(score01)
    return int(round(score01 * 100.0))
