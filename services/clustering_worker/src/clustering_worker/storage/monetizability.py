from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from domain.models.persona import Persona
from domain.scoring.monetizability import MonetizabilitySignal, compute_monetizability_score


@dataclass(frozen=True)
class InstanceForMonetizability:
    text: str
    persona: Optional[str] = None  # string stored on cluster or per-instance (if available)


def _parse_persona(p: Optional[str]) -> Optional[Persona]:
    if not p:
        return None
    try:
        return Persona(str(p))
    except Exception:
        return None


def compute_cluster_monetizability(instances: Iterable[InstanceForMonetizability]) -> int:
    signals = [
        MonetizabilitySignal(
            text=i.text or "",
            persona=_parse_persona(i.persona),
        )
        for i in instances
    ]
    return compute_monetizability_score(signals)
