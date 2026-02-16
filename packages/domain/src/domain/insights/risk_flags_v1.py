from typing import List


def generate_risk_flags(cluster) -> List[str]:
    flags = []

    contradiction = getattr(cluster, "contradiction_score", 0) or 0
    competitive_heat = getattr(cluster, "competitive_heat_score", 0) or 0
    saturation = getattr(cluster, "saturation_score", 0) or 0
    confidence = getattr(cluster, "confidence_score", 1) or 1

    if contradiction >= 4:
        flags.append("High internal signal contradiction")

    if competitive_heat >= 4:
        flags.append("High competition density")

    if saturation >= 4:
        flags.append("Trend showing early saturation")

    if confidence <= 0.4:
        flags.append("Low cluster confidence")

    return flags

