from __future__ import annotations

from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models import ClusterDailyMetric, ClusterSignal, PainCluster, PainInstance, Signal


def compute_for_day(
    db: Session,
    day: date,
    *,
    formula_version: str,
    cluster_version: str,
) -> list[dict]:
    q = (
        db.query(
            PainCluster.id.label("cluster_id"),
            func.count(ClusterSignal.id).label("frequency"),
            func.count(ClusterSignal.id).label("engagement"),
            func.avg(PainInstance.pain_score).label("avg_score"),
            func.count(func.distinct(Signal.source)).label("source_count"),
        )
        .join(ClusterSignal, ClusterSignal.cluster_id == PainCluster.id)
        .join(PainInstance, PainInstance.id == ClusterSignal.pain_instance_id)
        .join(Signal, Signal.id == PainInstance.signal_id)
        .filter(PainCluster.cluster_version == cluster_version)
        .filter(func.date(Signal.ingested_at) == day)
        .group_by(PainCluster.id)
    )

    rows = q.all()
    out: list[dict] = []
    for r in rows:
        out.append(
            {
                "cluster_id": int(r.cluster_id),
                "day": day,
                "formula_version": formula_version,
                "frequency": int(r.frequency or 0),
                "engagement": int(r.engagement or 0),
                "avg_score": float(r.avg_score or 0.0),
                "source_count": int(r.source_count or 0),
            }
        )
    return out


def upsert_metrics(
    db: Session,
    *,
    cluster_id: int,
    day: date,
    formula_version: str,
    frequency: int,
    engagement: int,
    avg_score: float,
    source_count: int,
    velocity: float,
    emerging: float,
    declining: float,
    score: float,
    score_volume: float,
    score_velocity: float,
    score_novelty: float,
    score_diversity: float,
    score_confidence: float,
) -> tuple[ClusterDailyMetric, bool]:
    obj = (
        db.query(ClusterDailyMetric)
        .filter(ClusterDailyMetric.cluster_id == cluster_id)
        .filter(ClusterDailyMetric.day == day)
        .filter(ClusterDailyMetric.formula_version == formula_version)
        .one_or_none()
    )

    if obj is None:
        obj = ClusterDailyMetric(
            cluster_id=cluster_id,
            day=day,
            formula_version=formula_version,
            frequency=frequency,
            engagement=engagement,
            avg_score=avg_score,
            source_count=source_count,
            velocity=velocity,
            emerging=emerging,
            declining=declining,
            score=score,
            score_volume=score_volume,
            score_velocity=score_velocity,
            score_novelty=score_novelty,
            score_diversity=score_diversity,
            score_confidence=score_confidence,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj, True

    changed = False
    fields = {
        "frequency": frequency,
        "engagement": engagement,
        "avg_score": avg_score,
        "source_count": source_count,
        "velocity": velocity,
        "emerging": emerging,
        "declining": declining,
        "score": score,
        "score_volume": score_volume,
        "score_velocity": score_velocity,
        "score_novelty": score_novelty,
        "score_diversity": score_diversity,
        "score_confidence": score_confidence,
    }
    for k, v in fields.items():
        if getattr(obj, k) != v:
            setattr(obj, k, v)
            changed = True

    if changed:
        db.add(obj)
        db.commit()
        db.refresh(obj)

    return obj, False


def get_prev_day(db: Session, *, cluster_id: int, day: date, formula_version: str):
    return (
        db.query(ClusterDailyMetric)
        .filter(ClusterDailyMetric.cluster_id == cluster_id)
        .filter(ClusterDailyMetric.day < day)
        .filter(ClusterDailyMetric.formula_version == formula_version)
        .order_by(ClusterDailyMetric.day.desc())
        .first()
    )
