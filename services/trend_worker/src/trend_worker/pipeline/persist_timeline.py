from __future__ import annotations

from datetime import date
from typing import Sequence

from trend_worker.timeline import DailyVolume, compute_timeline
from trend_worker.storage.cluster_daily_history import persist_cluster_daily_history


def persist_timeline_for_cluster(cluster_id: str, daily_volumes: Sequence[tuple[date, int]]) -> None:
    vols = [DailyVolume(day=d, volume=int(v)) for (d, v) in daily_volumes]
    timeline = compute_timeline(vols)

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

    persist_cluster_daily_history(cluster_id=cluster_id, timeline_rows=payload)
