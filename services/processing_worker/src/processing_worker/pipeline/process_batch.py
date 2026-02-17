from __future__ import annotations

from typing import Any

from processing_worker.settings import ALGO_VERSION
from processing_worker.features.extract_features import extract_features
from processing_worker.scoring import score_features
from processing_worker.storage.pain_instances_writer import write_pain_instance
from processing_worker.pipeline.load_signals import load_batch


def process_batch(*, signals: list[Any], vertical_db_id: int) -> dict[str, int]:
    created = 0
    skipped = 0

    for s in signals:
        # s is a SQLAlchemy Signal model (id, content, ...)
        content = getattr(s, "content", None)
        if not isinstance(content, str) or not content.strip():
            skipped += 1
            continue

        features = extract_features(content)
        score, breakdown = score_features(features)

        _, was_created = write_pain_instance(
            vertical_id=int(vertical_db_id),
            signal_id=int(getattr(s, "id")),
            algo_version=str(ALGO_VERSION),
            pain_score=float(score),
            breakdown=breakdown,
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    return {
        "signals": int(len(signals)),
        "pain_instances_created": int(created),
        "pain_instances_skipped": int(skipped),
    }


def process_signals_batch(job: dict[str, Any]) -> dict[str, int]:
    vertical_db_id = int(job.get("vertical_db_id") or 0)
    if vertical_db_id <= 0:
        return {"signals": 0, "pain_instances_created": 0, "pain_instances_skipped": 0}

    limit = job.get("limit")
    offset = job.get("offset")

    # Defaults: process all current signals for the vertical (safe for V0)
    limit_i = int(limit) if isinstance(limit, int) else 500
    offset_i = int(offset) if isinstance(offset, int) else 0

    signals = load_batch(vertical_db_id=vertical_db_id, limit=limit_i, offset=offset_i)
    return process_batch(signals=signals, vertical_db_id=vertical_db_id)
