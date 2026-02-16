from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal


Recommendation = Literal["STRONG_BUILD", "INVESTIGATE", "MONITOR", "IGNORE"]


@dataclass(frozen=True)
class BuildSignalInputs:
    exploitability_score: int
    exploitability_tier: str
    opportunity_window_status: str
    breakout_score: int
    confidence_score: int
    saturation_score: int
    contradiction_score: int


@dataclass(frozen=True)
class BuildSignal:
    recommendation: Recommendation
    reasoning_summary: str
    top_positive_factors: List[str]
    top_risk_factors: List[str]


def _recommendation_from_tier(tier: str) -> Recommendation:
    if tier == "STRONG_BUILD":
        return "STRONG_BUILD"
    if tier == "INVESTIGATE":
        return "INVESTIGATE"
    if tier == "MONITOR":
        return "MONITOR"
    return "IGNORE"


def compute_build_signal(inp: BuildSignalInputs) -> BuildSignal:
    positives: List[str] = []
    risks: List[str] = []

    # --- Positive signals ---
    if inp.exploitability_score >= 80:
        positives.append("High exploitability score")

    if inp.opportunity_window_status == "EARLY":
        positives.append("Early opportunity window")

    if inp.breakout_score > 0:
        positives.append("Active breakout detected")

    if inp.confidence_score >= 70:
        positives.append("High structural cluster confidence")

    # --- Risk signals ---
    if inp.saturation_score > 70:
        risks.append("High market saturation")

    if inp.contradiction_score > 50:
        risks.append("High signal contradiction")

    if inp.confidence_score < 40:
        risks.append("Low cluster reliability")

    # --- Recommendation ---
    recommendation = _recommendation_from_tier(inp.exploitability_tier)

    # Adjust recommendation downward if strong risk present
    if recommendation == "STRONG_BUILD" and len(risks) >= 2:
        recommendation = "INVESTIGATE"

    if recommendation in ("STRONG_BUILD", "INVESTIGATE") and inp.confidence_score < 30:
        recommendation = "MONITOR"

    # --- Reasoning summary ---
    if recommendation == "STRONG_BUILD":
        summary = "High momentum and structural strength."
    elif recommendation == "INVESTIGATE":
        summary = "Promising opportunity with some risk factors."
    elif recommendation == "MONITOR":
        summary = "Signal present but not strong enough yet."
    else:
        summary = "Weak or structurally risky cluster."

    return BuildSignal(
        recommendation=recommendation,
        reasoning_summary=summary,
        top_positive_factors=positives[:3],
        top_risk_factors=risks[:3],
    )
