from __future__ import annotations

from typing import Iterable

from db.session import SessionLocal
from db.repos import signals_vertical_auto as vertical_repo

from processing_worker.features.vertical_auto import compute_vertical_auto


def persist_signal_vertical_auto(signals: Iterable[object], *, threshold: float) -> None:
    db = SessionLocal()
    try:
        for s in signals:
            signal_id = getattr(s, "id", None)
            if signal_id is None:
                continue
            content = getattr(s, "content", "") or ""
            key, conf = compute_vertical_auto(content=content, threshold=threshold)
            vertical_repo.set_vertical_auto(
                db,
                signal_id=int(signal_id),
                vertical_auto=str(key),
                vertical_auto_confidence=int(conf),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
