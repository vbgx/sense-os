from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime
from typing import Iterable, Dict, List


@dataclass(frozen=True)
class ClusterSignal:
    cluster_id: str
    created_at: datetime


@dataclass(frozen=True)
class DailyAggregate:
    cluster_id: str
    day: str  # YYYY-MM-DD
    count: int


def aggregate_daily(signals: Iterable[ClusterSignal]) -> List[DailyAggregate]:
    """
    Deterministic daily aggregation of cluster signals.

    Input:
        Iterable of ClusterSignal(cluster_id, created_at)

    Output:
        List[DailyAggregate] sorted by (cluster_id, day)

    Rules:
        - Group by cluster_id
        - Group by calendar day (UTC assumed)
        - Count occurrences
        - Stable and reproducible
    """

    buckets: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for s in signals:
        if s.created_at is None:
            continue

        if not isinstance(s.created_at, datetime):
            continue

        day = s.created_at.date().isoformat()
        buckets[s.cluster_id][day] += 1

    result: List[DailyAggregate] = []

    for cluster_id in sorted(buckets.keys()):
        days = buckets[cluster_id]
        for day in sorted(days.keys()):
            result.append(
                DailyAggregate(
                    cluster_id=cluster_id,
                    day=day,
                    count=days[day],
                )
            )

    return result
