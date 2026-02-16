from __future__ import annotations

from db.session import SessionLocal
from db.repos import signals as signals_repo

from processing_worker.pipeline.persist_signal_language import persist_signal_language
from processing_worker.pipeline.persist_signal_quality import persist_signal_quality
from processing_worker.settings import SUPPORTED_LANGUAGES


def load_batch(vertical_id: int, limit: int, offset: int):
    db = SessionLocal()
    try:
        signals = signals_repo.list_by_vertical(
            db,
            vertical_id=vertical_id,
            limit=limit,
            offset=offset,
        )
    finally:
        db.close()

    persist_signal_language(signals)
    persist_signal_quality(signals)

    supported = set(SUPPORTED_LANGUAGES)
    out = []
    for s in signals:
        code = getattr(s, "language_code", None) or "unknown"
        if code in supported:
            out.append(s)
    return out
