from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

from db.models import ClusterDailyHistory
from db.repos.cluster_daily_history import upsert_history_rows


def persist_cluster_daily_history(
    cluster_id: str,
    timeline_rows: Iterable[dict],
) -> None:
    """
    timeline_rows: iterable of dicts with keys:
      day, volume, growth_rate, velocity, breakout_flag
    """
    rows = []
    for r in timeline_rows:
        day_val = r["day"]
        if isinstance(day_val, str):
            day_val = date.fromisoformat(day_val)
        elif isinstance(day_val, datetime):
            day_val = day_val.date()
        rows.append(
            ClusterDailyHistory(
                cluster_id=cluster_id,
                day=day_val,
                volume=int(r["volume"]),
                growth_rate=float(r["growth_rate"]),
                velocity=float(r["velocity"]),
                breakout_flag=bool(r["breakout_flag"]),
            )
        )
    upsert_history_rows(rows)
