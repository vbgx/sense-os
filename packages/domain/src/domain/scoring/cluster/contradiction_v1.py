from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from domain.scoring.contradiction import ContradictionSignal, compute_contradiction_index


@dataclass(frozen=True)
class InstanceForContradiction:
    sentiment_compound: Optional[float]
    created_at: Optional[datetime]


def compute_cluster_contradiction(instances: Iterable[InstanceForContradiction]) -> int:
    signals = [
        ContradictionSignal(
            sentiment_compound=i.sentiment_compound,
            created_at=i.created_at,
        )
        for i in instances
    ]
    return compute_contradiction_index(signals)
