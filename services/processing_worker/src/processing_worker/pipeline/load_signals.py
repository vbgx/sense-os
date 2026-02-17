from __future__ import annotations

from db.session import SessionLocal
from db.repos import signals as signals_repo

from processing_worker.pipeline.persist_signal_language import persist_signal_language
from processing_worker.pipeline.persist_signal_quality import persist_signal_quality
from processing_worker.pipeline.persist_signal_spam import persist_signal_spam
from processing_worker.pipeline.persist_signal_vertical_auto import persist_signal_vertical_auto
from processing_worker.settings import SUPPORTED_LANGUAGES, SPAM_THRESHOLD, VERTICAL_CLASSIFIER_THRESHOLD


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
    persist_signal_spam(signals)
    persist_signal_vertical_auto(signals, threshold=VERTICAL_CLASSIFIER_THRESHOLD)

    db2 = SessionLocal()
    try:
        refreshed = signals_repo.list_by_vertical(
            db2,
            vertical_id=vertical_id,
            limit=limit,
            offset=offset,
        )
    finally:
        db2.close()

    supported = set(SUPPORTED_LANGUAGES)
    out = []
    for s in refreshed:
        if getattr(s, "language_code", None) not in supported:
            continue
        if (getattr(s, "spam_score", 0) or 0) >= int(SPAM_THRESHOLD):
            continue
        out.append(s)
    return out
