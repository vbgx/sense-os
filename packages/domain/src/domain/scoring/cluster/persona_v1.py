from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from domain.models.persona import PersonaInference
from domain.scoring.persona_inference import PersonaSignal, infer_cluster_persona


@dataclass(frozen=True)
class InstanceForPersona:
    text: str


def infer_cluster_persona_from_instances(instances: Iterable[InstanceForPersona]) -> PersonaInference:
    signals = [PersonaSignal(text=i.text or "") for i in instances]
    return infer_cluster_persona(signals)
