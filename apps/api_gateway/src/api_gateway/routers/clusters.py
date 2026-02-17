from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List
import json

from api_gateway.dependencies import get_clusters_use_case
from application.ports import NotFoundError
from application.use_cases.clusters import ClustersUseCase

router = APIRouter(prefix="/clusters", tags=["clusters"])


# ----------------------
# Pydantic schemas
# ----------------------
class ClusterOut(BaseModel):
    id: int
    title: str
    size: int
    cluster_summary: str | None
    key_phrases: list[str]
    top_signal_ids: list[int]
    confidence_score: int


class ClusterListOut(BaseModel):
    total: int
    items: list[ClusterOut]
    limit: int
    offset: int


class TimelinePointOut(BaseModel):
    date: str
    volume: int
    growth_rate: float
    velocity: float
    breakout_flag: bool


# ----------------------
# Endpoints
# ----------------------
@router.get("", response_model=ClusterListOut)
def list_clusters(
    vertical_id: int = Query(..., description="Vertical ID to fetch clusters for"),
    min_exploitability: int | None = Query(None, ge=0, le=100),
    max_exploitability: int | None = Query(None, ge=0, le=100),
    spam: bool = Query(False, description="Include clusters marked as spam"),
    order_by: str = Query("size", description="Column to order by, e.g., size, exploitability_score"),
    desc: bool = Query(True, description="Sort descending"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    use_case: ClustersUseCase = Depends(get_clusters_use_case),
):
    """Return paginated clusters with UX fields"""

    def _to_int(v, default: int = 0) -> int:
        try:
            return int(v)
        except Exception:
            return default

    rows = use_case.list_clusters(
        vertical_id=vertical_id,
        min_exploitability=min_exploitability,
        max_exploitability=max_exploitability,
        order_by=None,
        desc=desc,
    )

    if not spam:
        rows = [r for r in rows if not bool(getattr(r, "is_spam", False))]

    order_key = order_by or "size"
    rows = sorted(rows, key=lambda r: _to_int(getattr(r, order_key, 0)), reverse=bool(desc))

    total = len(rows)
    rows = rows[offset : offset + limit]

    def cluster_to_dict(c) -> ClusterOut:
        return ClusterOut(
            id=c.id,
            title=c.title,
            size=c.size,
            cluster_summary=c.cluster_summary,
            key_phrases=json.loads(getattr(c, "key_phrases_json", "[]") or "[]"),
            top_signal_ids=json.loads(getattr(c, "top_signal_ids_json", "[]") or "[]"),
            confidence_score=c.confidence_score,
        )

    return ClusterListOut(total=total, items=[cluster_to_dict(c) for c in rows], limit=limit, offset=offset)


@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: int, use_case: ClustersUseCase = Depends(get_clusters_use_case)) -> ClusterOut:
    """Return single cluster details"""
    try:
        c = use_case.get_cluster(str(cluster_id))
    except (NotFoundError, KeyError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ClusterOut(
        id=c.id,
        title=c.title,
        size=c.size,
        cluster_summary=c.cluster_summary,
        key_phrases=json.loads(getattr(c, "key_phrases_json", "[]") or "[]"),
        top_signal_ids=json.loads(getattr(c, "top_signal_ids_json", "[]") or "[]"),
        confidence_score=c.confidence_score,
    )


@router.get("/{cluster_id}/timeline", response_model=list[TimelinePointOut])
def get_cluster_timeline(
    cluster_id: int,
    days: int = Query(90, ge=1, le=3650, description="Number of days to fetch"),
    use_case: ClustersUseCase = Depends(get_clusters_use_case),
) -> list[TimelinePointOut]:
    """Return cluster metrics over time"""
    rows = use_case.list_cluster_timeline(cluster_id=str(cluster_id), days=days)

    return [
        TimelinePointOut(
            date=r.day.isoformat(),
            volume=r.volume,
            growth_rate=r.growth_rate,
            velocity=r.velocity,
            breakout_flag=r.breakout_flag,
        )
        for r in rows
    ]
