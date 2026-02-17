from __future__ import annotations

from typing import Iterable

from db.session import SessionLocal
from db.repos import signals as signals_repo

from processing_worker.features.spam import compute_spam


def persist_signal_spam(signals: Iterable[object]) -> None:
    db = SessionLocal()
    try:
        for s in signals:
            signal_id = getattr(s, "id", None)
            if signal_id is None:
                continue
            content = getattr(s, "content", "") or ""
            score = compute_spam(content=content)
            signals_repo.set_spam_score(
                db,
                signal_id=int(signal_id),
                spam_score=int(score),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
