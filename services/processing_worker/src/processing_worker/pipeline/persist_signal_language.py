from __future__ import annotations

from typing import Iterable

from db.session import SessionLocal
from db.repos import signals as signals_repo

from processing_worker.features.language import compute_language_code


def persist_signal_language(signals: Iterable[object]) -> None:
    db = SessionLocal()
    try:
        for s in signals:
            signal_id = getattr(s, "id", None)
            if signal_id is None:
                continue
            content = getattr(s, "content", "") or ""
            code = compute_language_code(content=content)
            signals_repo.set_language_code(db, signal_id=int(signal_id), language_code=str(code))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
