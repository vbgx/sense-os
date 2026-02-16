from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import ClusterDailyHistory


@dataclass(frozen=True)
class ClusterTimelinePoint:
    day: date
    volume: int
    growth_rate: float
    velocity: float
    breakout_flag: bool


class ClusterDailyHistoryAdapter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_cluster_history(self, *, cluster_id: str, days: int) -> list[ClusterTimelinePoint]:
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
        res = self._session.execute(stmt).all()

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
