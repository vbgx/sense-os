from dataclasses import dataclass


@dataclass
class MonetizationAngleResult:
    model: str
    pricing_power_estimate: str
    rationale: str


def generate_monetization_angle(cluster, target_persona: str):
    score = getattr(cluster, "monetizability_score", 0) or 0
    context = (
        (cluster.cluster_summary or "") + " " + " ".join(cluster.key_phrases or [])
    ).lower()

    persona_lower = target_persona.lower()

    # Default values
    model = "subscription"
    pricing_power = "medium"
    rationale = "Recurring friction suggests recurring value capture."

    # High monetizability logic
    if score >= 4:
        pricing_power = "high"

        if "api" in context or "integration" in context:
            model = "api-based"
            rationale = "Technical integration context supports API monetization."
        elif "team" in persona_lower or "operators" in persona_lower:
            model = "per-seat"
            rationale = "Team-based workflow suggests per-seat pricing."
        elif "usage" in context or "volume" in context:
            model = "usage-based"
            rationale = "Variable usage intensity aligns with usage-based pricing."
        else:
            model = "subscription"
            rationale = "High recurring pain supports SaaS subscription model."

    # Medium monetizability logic
    elif 2 <= score < 4:
        pricing_power = "medium"

        if "add-on" in context or "extension" in context:
            model = "premium add-on"
            rationale = "Complementary workflow suggests add-on monetization."
        elif "volume" in context:
            model = "usage-based"
            rationale = "Moderate volume dependency supports usage pricing."
        else:
            model = "subscription"
            rationale = "Persistent pain supports subscription model."

    # Low monetizability logic
    else:
        pricing_power = "low"
        model = "one-off"
        rationale = "Low recurring intensity suggests one-off value capture."

    return MonetizationAngleResult(
        model=model,
        pricing_power_estimate=pricing_power,
        rationale=rationale
    )

