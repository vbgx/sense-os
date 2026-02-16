from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class BuildHypothesisInputs:
    dominant_persona: str
    cluster_summary: str
    key_phrases: List[str]
    exploitability_tier: str
    breakout_score: int
    contradiction_score: int


@dataclass(frozen=True)
class BuildHypothesis:
    target_persona: str
    core_pain_statement: str
    suggested_micro_solution: str
    early_validation_path: str
    risk_flags: List[str]


def _micro_solution_from_phrase(phrase: str) -> str:
    return f"Lightweight tool solving '{phrase}' via automation or workflow simplification."


def compute_build_hypothesis(inp: BuildHypothesisInputs) -> BuildHypothesis:
    key_phrase = inp.key_phrases[0] if inp.key_phrases else inp.cluster_summary

    core_pain = f"{inp.dominant_persona} struggle with {key_phrase.lower()}."

    suggested_solution = _micro_solution_from_phrase(key_phrase)

    validation_path = (
        f"Interview 10 {inp.dominant_persona.lower()} experiencing '{key_phrase}'. "
        "Offer clickable mock or manual concierge solution."
    )

    risks: List[str] = []

    if inp.contradiction_score > 50:
        risks.append("High signal contradiction")

    if inp.exploitability_tier in ("MONITOR", "IGNORE"):
        risks.append("Low exploitability tier")

    if inp.breakout_score == 0:
        risks.append("No breakout momentum")

    return BuildHypothesis(
        target_persona=inp.dominant_persona,
        core_pain_statement=core_pain,
        suggested_micro_solution=suggested_solution,
        early_validation_path=validation_path,
        risk_flags=risks,
    )
