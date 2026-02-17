from __future__ import annotations

from datetime import date
from collections import defaultdict
from typing import Iterable, Dict, List

from trend_worker.timeline import DailyVolume, compute_timeline
from trend_worker.storage.cluster_daily_history import persist_cluster_daily_history
from trend_worker.pipeline.aggregate_daily import DailyAggregate


def persist_timeline_from_daily_aggregate(
    aggregates: Iterable[DailyAggregate],
) -> None:
    """
    Takes output of aggregate_daily() and:
      - groups by cluster_id
      - computes timeline metrics
      - persists into cluster_daily_history

    Fully deterministic.
    Idempotent due to (cluster_id, day) PK.
    """

    grouped: Dict[str, List[DailyAggregate]] = defaultdict(list)

    for agg in aggregates:
        grouped[agg.cluster_id].append(agg)

    for cluster_id, rows in grouped.items():
        daily_volumes = [
            DailyVolume(
                day=date.fromisoformat(r.day),
                volume=int(r.count),
            )
            for r in sorted(rows, key=lambda x: x.day)
        ]

        timeline = compute_timeline(daily_volumes)

        payload = [
            {
                "day": p.day,
                "volume": p.volume,
                "growth_rate": p.growth_rate,
                "velocity": p.velocity,
                "breakout_flag": p.breakout_flag,
            }
            for p in timeline
        ]

        persist_cluster_daily_history(
            cluster_id=cluster_id,
            timeline_rows=payload,
        )
