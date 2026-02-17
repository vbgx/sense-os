from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Persona(str, Enum):
    founder = "founder"
    operator = "operator"
    freelancer = "freelancer"
    enterprise_employee = "enterprise_employee"
    hobbyist = "hobbyist"
    unknown = "unknown"


@dataclass(frozen=True)
class PersonaInference:
    dominant_persona: Persona
    confidence: float  # 0..1
    distribution: dict[Persona, float]  # 0..1, sums to ~1
