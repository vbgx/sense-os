from __future__ import annotations

from typing import Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.models import PainInstance, Signal


def create_if_absent(db: Session, **kwargs) -> Tuple[PainInstance, bool]:
    """
    Strictly idempotent create for PainInstance.

    Natural identity: (algo_version, breakdown_hash).
    Database enforces it via uq_pain_instances_algo_breakdown.

    Implementation: try INSERT (commit). If UNIQUE conflict -> rollback -> SELECT existing.
    This is atomic and safe under concurrency and reruns.
    """
    vertical_id = int(kwargs["vertical_id"])
    signal_id = int(kwargs["signal_id"])
    algo_version = str(kwargs.get("algo_version", ""))
    breakdown_hash = str(kwargs.get("breakdown_hash", ""))
    if not breakdown_hash:
        raise ValueError("breakdown_hash is required for idempotent create")

    obj = PainInstance(
        vertical_id=vertical_id,
        signal_id=signal_id,
        algo_version=algo_version,
        pain_score=float(kwargs.get("pain_score", 0.0)),
        breakdown=kwargs.get("breakdown"),
        breakdown_hash=breakdown_hash,
    )

    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj, True
    except IntegrityError:
        # Someone already inserted it (previous run or concurrent worker)
        db.rollback()

    existing = (
        db.query(PainInstance)
        .filter(PainInstance.algo_version == algo_version)
        .filter(PainInstance.breakdown_hash == breakdown_hash)
        .one()
    )
    return existing, False


def list_ranked(*, db: Session, limit: int, offset: int, vertical_id: int):
    from sqlalchemy import func

    if vertical_id is None:
        raise ValueError("vertical_id is required")

    q = (
        db.query(PainInstance, Signal)
        .join(Signal, Signal.id == PainInstance.signal_id)
        .filter(PainInstance.vertical_id == int(vertical_id))
        .order_by(PainInstance.pain_score.desc(), PainInstance.id.asc())
        .limit(int(limit))
        .offset(int(offset))
    )
    rows = q.all()

    total = (
        db.query(func.count(PainInstance.id))
        .filter(PainInstance.vertical_id == int(vertical_id))
        .scalar()
        or 0
    )
    return rows, int(total)


def get_with_signal(*, db: Session, pain_id: int):
    q = (
        db.query(PainInstance, Signal)
        .join(Signal, Signal.id == PainInstance.signal_id)
        .filter(PainInstance.id == int(pain_id))
    )
    return q.one_or_none()
