from __future__ import annotations

import logging
import os
from typing import Any, Iterable, Tuple

from db.repos import pain_instances as repo
from db.session import SessionLocal
from processing_worker.storage.dedup import breakdown_hash

log = logging.getLogger(__name__)


def _debug_enabled() -> bool:
    return os.getenv("PROCESSING_DEBUG") == "1" or os.getenv("SENSE_DEBUG") == "1"


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


class PainInstancesWriter:
    def __init__(self) -> None:
        self._Session = SessionLocal

    def persist_many(self, pain_instances: Iterable[dict]) -> int:
        rows = list(pain_instances)
        if not rows:
            if _debug_enabled():
                log.info("pain_instances_persist_debug empty_rows=1")
            return 0

        created = 0
        reasons: dict[str, int] = {
            "missing_signal_id": 0,
            "missing_vertical_id": 0,
            "missing_pain_score": 0,
            "missing_breakdown": 0,
            "db_conflict_or_exists": 0,
            "created": 0,
        }

        with self._Session() as db:
            for item in rows:
                try:
                    signal_id = item.get("signal_id")
                    vertical_id = item.get("vertical_db_id") or item.get("vertical_id")
                    pain_score = item.get("pain_score")

                    if signal_id is None:
                        reasons["missing_signal_id"] += 1
                        continue
                    if vertical_id is None:
                        reasons["missing_vertical_id"] += 1
                        continue
                    if pain_score is None:
                        reasons["missing_pain_score"] += 1
                        continue

                    algo_version = str(item.get("algo_version") or "heuristics_v1")

                    breakdown = item.get("breakdown")
                    if breakdown is None:
                        # allow default breakdown but count missing
                        reasons["missing_breakdown"] += 1
                        breakdown = {}

                    if not isinstance(breakdown, dict):
                        reasons["missing_breakdown"] += 1
                        breakdown = {}

                    # enforce stable keys
                    breakdown.setdefault("signal_id", int(signal_id))

                    _, was_created = repo.create_if_absent(
                        db,
                        vertical_id=int(vertical_id),
                        signal_id=int(signal_id),
                        algo_version=algo_version,
                        pain_score=float(pain_score),
                        breakdown=breakdown,
                        breakdown_hash=breakdown_hash(breakdown),
                    )
                    if was_created:
                        created += 1
                        reasons["created"] += 1
                    else:
                        reasons["db_conflict_or_exists"] += 1

                except Exception as exc:
                    # Don't silently swallow unexpected errors.
                    # If this triggers, we want to see it immediately.
                    log.exception("pain_instances_persist_debug error=%s item=%s", exc, item)
                    raise

        if _debug_enabled():
            sample = rows[0] if rows else None
            log.info(
                "pain_instances_persist_debug rows=%s created=%s reasons=%s sample=%s",
                len(rows),
                int(created),
                reasons,
                sample,
            )

        return int(created)
