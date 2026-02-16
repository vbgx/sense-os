from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional

from domain.models.persona import Persona


@dataclass(frozen=True)
class MonetizabilitySignal:
    text: str
    persona: Optional[Persona] = None  # optional per-signal persona (if available)


# High-precision business / monetization lexicon (expand iteratively)
BUSINESS_MARKERS_STRONG = [
    "revenue",
    "lost revenue",
    "revenue loss",
    "mrr",
    "arr",
    "sales",
    "pipeline",
    "customers",
    "client churn",
    "churn",
    "conversion",
    "pricing",
    "invoice",
    "billing",
    "payment",
    "payout",
    "cash flow",
    "cashflow",
    "profit",
    "margin",
    "budget",
    "cost of",
    "operational",
    "ops",
    "downtime",
    "incident",
    "sla",
]

BUSINESS_MARKERS_WEAK = [
    "pay",
    "paid",
    "charge",
    "fee",
    "cost",
    "expensive",
    "spend",
    "time lost",
    "wasting time",
    "hours",
    "manual",
    "inefficient",
    "workflow",
    "process",
    "compliance",
    "procurement",
    "stakeholders",
]

# Phrases that often indicate "hobby frustration" rather than monetizable pain
HOBBY_DEBOOST_MARKERS = [
    "for fun",
    "just learning",
    "learning project",
    "side project",
    "toy project",
    "beginner",
    "home lab",
    "homelab",
    "tutorial",
]


PERSONA_WEIGHTS: dict[Persona, float] = {
    Persona.founder: 1.20,
    Persona.operator: 1.05,
    Persona.freelancer: 1.10,
    Persona.enterprise_employee: 1.00,
    Persona.hobbyist: 0.70,
    Persona.unknown: 0.90,
}


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _log_norm(x: float, cap: float) -> float:
    if cap <= 0:
        return 0.0
    return _clamp01(math.log1p(max(0.0, x)) / math.log1p(cap))


def _count_markers(text: str, markers: list[str]) -> int:
    t = (text or "").lower()
    return sum(1 for m in markers if m in t)


def compute_monetizability_score(
    signals: Iterable[MonetizabilitySignal],
    *,
    # weights between components
    w_business: float = 0.55,
    w_revenue_context: float = 0.25,
    w_efficiency: float = 0.20,
    # caps for log normalization
    cap_business_hits: float = 25.0,
    cap_revenue_hits: float = 15.0,
    cap_efficiency_hits: float = 20.0,
) -> int:
    """
    Monetizability Proxy Score (0..100), cluster-level.

    Heuristic components:
    - Business-related context (strong + weak markers)
    - Revenue-specific context (subset: revenue/billing/payment/churn etc.)
    - Operational inefficiency context (time lost/manual/inefficient etc.)
    Persona weight boosts founders/freelancers and deboosts hobbyists.

    This is intentionally a proxy (not TAM/pricing). It is:
    - deterministic
    - stable on rerun
    - bounded 0..100
    """
    items = list(signals)
    if not items:
        return 0

    business_hits = 0
    revenue_hits = 0
    efficiency_hits = 0
    hobby_deboost_hits = 0

    # If per-signal persona exists, use it; else neutral weighting.
    persona_weights = []

    for s in items:
        t = s.text or ""
        business_hits += 3 * _count_markers(t, BUSINESS_MARKERS_STRONG)
        business_hits += 1 * _count_markers(t, BUSINESS_MARKERS_WEAK)

        # Revenue-specific subset (higher intent)
        revenue_hits += _count_markers(
            t,
            [
                "revenue",
                "lost revenue",
                "revenue loss",
                "mrr",
                "arr",
                "billing",
                "invoice",
                "payment",
                "payout",
                "cash flow",
                "cashflow",
                "margin",
                "profit",
                "churn",
                "conversion",
                "pricing",
            ],
        )

        # Efficiency / ops pain subset
        efficiency_hits += _count_markers(
            t,
            [
                "time lost",
                "wasting time",
                "manual",
                "inefficient",
                "workflow",
                "process",
                "operational",
                "ops",
                "downtime",
                "incident",
                "sla",
            ],
        )

        hobby_deboost_hits += _count_markers(t, HOBBY_DEBOOST_MARKERS)

        if s.persona is not None:
            persona_weights.append(PERSONA_WEIGHTS.get(s.persona, 0.90))

    business = _log_norm(float(business_hits), cap_business_hits)
    revenue = _log_norm(float(revenue_hits), cap_revenue_hits)
    efficiency = _log_norm(float(efficiency_hits), cap_efficiency_hits)

    ratio = (w_business * business) + (w_revenue_context * revenue) + (w_efficiency * efficiency)
    ratio = _clamp01(ratio)

    # Apply persona weighting at cluster-level (mean), if available
    if persona_weights:
        pw = sum(persona_weights) / float(len(persona_weights))
        ratio = _clamp01(ratio * pw)

    # Deboost if strong hobby cues dominate
    # (keeps "fun/learning" clusters from being mis-scored as monetizable)
    if hobby_deboost_hits > 0 and (business_hits + revenue_hits + efficiency_hits) <= 2:
        ratio = _clamp01(ratio * 0.35)

    return int(round(100.0 * ratio))
