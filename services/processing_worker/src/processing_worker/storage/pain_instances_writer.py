from __future__ import annotations

from typing import Any, Iterable, Tuple

from db.repos import pain_instances as repo
from processing_worker.storage.dedup import breakdown_hash


def write_pain_instance_in_session(
    *,
    db: Any,
    vertical_id: int,
    signal_id: int,
    algo_version: str,
    pain_score: float,
    breakdown: Any,
) -> Tuple[object, bool]:
    """
    Returns (obj, created).

    Uses the provided DB session (no open/close here).
    Idempotence is enforced by DB unique constraint (algo_version, breakdown_hash)
    and repo.create_if_absent() handles conflicts atomically.
    """
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


def write_pain_instances_bulk_in_session(
    *,
    db: Any,
    envelopes: Iterable[Any],
    algo_version: str,
) -> tuple[int, int]:
    """
    Returns (created, skipped).
    Assumes each envelope has: vertical_db_id, signal_id, pain_score, breakdown.
    """
    created = 0
    skipped = 0

    for e in envelopes:
        if e.pain_score is None or e.breakdown is None:
            skipped += 1
            continue

        _, was_created = write_pain_instance_in_session(
            db=db,
            vertical_id=int(e.vertical_db_id),
            signal_id=int(e.signal_id),
            algo_version=str(algo_version),
            pain_score=float(e.pain_score),
            breakdown=e.breakdown,
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    return int(created), int(skipped)
