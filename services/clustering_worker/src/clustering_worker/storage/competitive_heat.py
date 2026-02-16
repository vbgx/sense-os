from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from domain.scoring.competitive_heat import CompetitiveHeatSignal, compute_competitive_heat_score


@dataclass(frozen=True)
class InstanceForCompetitiveHeat:
    text: str


def compute_cluster_competitive_heat(instances: Iterable[InstanceForCompetitiveHeat]) -> int:
    signals = [CompetitiveHeatSignal(text=i.text or "") for i in instances]
    return compute_competitive_heat_score(signals)
