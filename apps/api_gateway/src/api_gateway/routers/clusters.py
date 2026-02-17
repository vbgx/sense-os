from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.session import SessionLocal
from db.models import PainCluster, ClusterDailyMetric
from pydantic import BaseModel
from typing import List
import json

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
# Dependencies
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    db: Session = Depends(get_db),
):
    """Return paginated clusters with UX fields"""
    filters = [PainCluster.vertical_id == vertical_id]
    if min_exploitability is not None:
        filters.append(PainCluster.exploitability_score >= min_exploitability)
    if max_exploitability is not None:
        filters.append(PainCluster.exploitability_score <= max_exploitability)
    if not spam and hasattr(PainCluster, "is_spam"):
        filters.append(getattr(PainCluster, "is_spam") == False)

    query = db.query(PainCluster).filter(and_(*filters))

    # ordering
    order_col = getattr(PainCluster, order_by, PainCluster.size)
    query = query.order_by(order_col.desc() if desc else order_col.asc())

    # pagination
    rows = query.offset(offset).limit(limit).all()
    total = db.query(PainCluster).filter(and_(*filters)).count()

    def cluster_to_dict(c: PainCluster):
        return ClusterOut(
            id=c.id,
            title=c.title,
            size=c.size,
            cluster_summary=c.cluster_summary,
            key_phrases=json.loads(c.key_phrases_json or "[]"),
            top_signal_ids=json.loads(c.top_signal_ids_json or "[]"),
            confidence_score=c.confidence_score,
        )

    return ClusterListOut(
        total=total,
        items=[cluster_to_dict(c) for c in rows],
        limit=limit,
        offset=offset,
    )


@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)) -> ClusterOut:
    """Return single cluster details"""
    c = db.query(PainCluster).filter(PainCluster.id == cluster_id).first()
    if not c:
        return {}
    return ClusterOut(
        id=c.id,
        title=c.title,
        size=c.size,
        cluster_summary=c.cluster_summary,
        key_phrases=json.loads(c.key_phrases_json or "[]"),
        top_signal_ids=json.loads(c.top_signal_ids_json or "[]"),
        confidence_score=c.confidence_score,
    )


@router.get("/{cluster_id}/timeline", response_model=list[TimelinePointOut])
def get_cluster_timeline(
    cluster_id: int,
    days: int = Query(90, ge=1, le=3650, description="Number of days to fetch"),
    db: Session = Depends(get_db),
) -> list[TimelinePointOut]:
    """Return cluster metrics over time"""
    rows = (
        db.query(ClusterDailyMetric)
        .filter(ClusterDailyMetric.cluster_id == cluster_id)
        .order_by(ClusterDailyMetric.day.asc())
        .limit(days)
        .all()
    )

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
