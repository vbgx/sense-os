from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from domain.scoring.recurrence import RecurrenceSignal, compute_recurrence


@dataclass(frozen=True)
class InstanceForRecurrence:
    text: str
    user_id: Optional[str]
    source_id: Optional[str]
    created_at: Optional[datetime]


def compute_cluster_recurrence(instances: Iterable[InstanceForRecurrence]) -> tuple[int, float]:
    signals = [
        RecurrenceSignal(
            text=i.text or "",
            user_id=i.user_id,
            source_id=i.source_id,
            created_at=i.created_at,
        )
        for i in instances
    ]
    return compute_recurrence(signals)
