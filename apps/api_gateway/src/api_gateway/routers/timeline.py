from __future__ import annotations

from fastapi import APIRouter, Query

from db.repos.cluster_daily_history import list_cluster_history
from api_gateway.schemas.timeline import TimelinePointOut

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("/{cluster_id}/timeline", response_model=list[TimelinePointOut])
def get_cluster_timeline(
    cluster_id: str,
    days: int = Query(default=90, ge=1, le=3650),
) -> list[TimelinePointOut]:
    rows = list_cluster_history(cluster_id=cluster_id, days=days)
    return [
        TimelinePointOut(
            date=r.day,
            volume=r.volume,
            growth_rate=r.growth_rate,
            velocity=r.velocity,
            breakout_flag=r.breakout_flag,
        )
        for r in rows
    ]
