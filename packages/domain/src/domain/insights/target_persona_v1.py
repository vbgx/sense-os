from dataclasses import dataclass
from typing import List
import re


@dataclass
class TargetPersonaResult:
    primary_persona: str
    confidence_score: float
    supporting_personas: List[str]


_STAGE_RULES = {
    "early-stage": ["early", "just launched", "new store"],
    "scaling": ["scaling", "growing fast", "rapid growth"],
}

_PLATFORM_RULES = {
    "Shopify": ["shopify"],
    "Amazon sellers": ["amazon"],
    "Etsy sellers": ["etsy"],
    "SaaS": ["saas"],
    "Agency": ["agency"],
}

_FRICTION_RULES = {
    "returns-heavy": ["return", "refund"],
    "high-churn": ["churn"],
    "support-overloaded": ["support overload", "too many tickets"],
    "compliance-constrained": ["compliance", "regulation"],
}

_PLURAL_MAP = {
    "founder": "founders",
    "operator": "operators",
    "freelancer": "freelancers",
    "developer": "developers",
}


def _contains_any(text: str, keywords: List[str]) -> bool:
    text = text.lower()
    return any(k in text for k in keywords)


def generate_target_persona(cluster) -> TargetPersonaResult:
    dominant = cluster.dominant_persona
    key_phrases = " ".join(cluster.key_phrases or []).lower()
    signals = " ".join(cluster.representative_signals or []).lower()

    combined = key_phrases + " " + signals

    # Stage
    stage_label = ""
    for stage, keywords in _STAGE_RULES.items():
        if _contains_any(combined, keywords):
            stage_label = stage.capitalize()
            break

    # Platform
    platform_label = ""
    for platform, keywords in _PLATFORM_RULES.items():
        if _contains_any(combined, keywords):
            platform_label = platform
            break

    # Friction
    friction_label = ""
    for friction, keywords in _FRICTION_RULES.items():
        if _contains_any(combined, keywords):
            friction_label = friction
            break

    persona_plural = _PLURAL_MAP.get(dominant, dominant + "s")

    parts = []

    if stage_label:
        parts.append(stage_label)

    if platform_label:
        parts.append(platform_label)

    parts.append(persona_plural)

    if friction_label:
        parts.append(friction_label)

    primary = " ".join(parts)

    confidence = 0.7
    if platform_label:
        confidence += 0.1
    if friction_label:
        confidence += 0.1

    confidence = min(confidence, 1.0)

    return TargetPersonaResult(
        primary_persona=primary,
        confidence_score=confidence,
        supporting_personas=[],
    )

