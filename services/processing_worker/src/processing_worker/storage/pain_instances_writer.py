from __future__ import annotations

from typing import Any, Tuple

from db.session import SessionLocal
from db.repos import pain_instances as repo

from processing_worker.storage.dedup import breakdown_hash


def write_pain_instance(
    *,
    vertical_id: int,
    signal_id: int,
    algo_version: str,
    pain_score: float,
    breakdown: Any,
) -> Tuple[object, bool]:
    """
    Returns (obj, created).
    Strict idempotence is enforced by DB unique constraint (algo_version, breakdown_hash)
    and repo.create_if_absent() handles conflicts atomically.
    """
    db = SessionLocal()
    try:
        breakdown_h = breakdown_hash(breakdown)
        obj, created = repo.create_if_absent(
            db,
            vertical_id=int(vertical_id),
            signal_id=int(signal_id),
            algo_version=str(algo_version),
            pain_score=float(pain_score),
            breakdown=breakdown,
            breakdown_hash=breakdown_h,
        )
        return obj, created
    finally:
        db.close()
