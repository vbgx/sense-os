from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from sqlalchemy import select

from db.models import ClusterDailyHistory
from db.session import session_scope


@dataclass(frozen=True)
class ClusterTimelinePoint:
    day: date
    volume: int
    growth_rate: float
    velocity: float
    breakout_flag: bool


def upsert_history_rows(rows: Iterable[ClusterDailyHistory]) -> None:
    # ORM merge is deterministic and idempotent for (cluster_id, day)
    with session_scope() as s:
        for r in rows:
            s.merge(r)


def list_cluster_history(cluster_id: str, days: int = 90) -> list[ClusterTimelinePoint]:
    with session_scope() as s:
        stmt = (
            select(
                ClusterDailyHistory.day,
                ClusterDailyHistory.volume,
                ClusterDailyHistory.growth_rate,
                ClusterDailyHistory.velocity,
                ClusterDailyHistory.breakout_flag,
            )
            .where(ClusterDailyHistory.cluster_id == cluster_id)
            .order_by(ClusterDailyHistory.day.asc())
        )
        res = s.execute(stmt).all()

    points = [
        ClusterTimelinePoint(
            day=r.day,
            volume=int(r.volume),
            growth_rate=float(r.growth_rate),
            velocity=float(r.velocity),
            breakout_flag=bool(r.breakout_flag),
        )
        for r in res
    ]

    if days and int(days) > 0:
        return points[-int(days):]
    return points
