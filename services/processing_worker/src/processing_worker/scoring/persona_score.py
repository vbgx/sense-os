from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from domain.models.persona import Persona
from domain.scoring.persona_inference import score_persona_for_signal


@dataclass(frozen=True)
class PersonaScore:
    founder: float
    operator: float
    freelancer: float
    enterprise_employee: float
    hobbyist: float
    unknown: float

    def dominant(self) -> Persona:
        items = {
            Persona.founder: self.founder,
            Persona.operator: self.operator,
            Persona.freelancer: self.freelancer,
            Persona.enterprise_employee: self.enterprise_employee,
            Persona.hobbyist: self.hobbyist,
            Persona.unknown: self.unknown,
        }
        return max(items.items(), key=lambda kv: kv[1])[0]


def compute_persona_score(text: str) -> PersonaScore:
    raw = score_persona_for_signal(text)
    return PersonaScore(
        founder=float(raw.get(Persona.founder, 0.0)),
        operator=float(raw.get(Persona.operator, 0.0)),
        freelancer=float(raw.get(Persona.freelancer, 0.0)),
        enterprise_employee=float(raw.get(Persona.enterprise_employee, 0.0)),
        hobbyist=float(raw.get(Persona.hobbyist, 0.0)),
        unknown=float(raw.get(Persona.unknown, 0.0)),
    )
