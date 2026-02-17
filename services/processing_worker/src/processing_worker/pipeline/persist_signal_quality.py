from __future__ import annotations

from typing import Iterable

from db.session import SessionLocal
from db.repos import signals as signals_repo

from processing_worker.features.signal_quality import compute_quality


def persist_signal_quality(signals: Iterable[object]) -> None:
    db = SessionLocal()
    try:
        for s in signals:
            signal_id = getattr(s, "id", None)
            if signal_id is None:
                continue
            content = getattr(s, "content", "") or ""
            created_at = getattr(s, "created_at", None)
            score = compute_quality(content=content, created_at=created_at)
            signals_repo.set_signal_quality_score(
                db,
                signal_id=int(signal_id),
                signal_quality_score=int(score),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
