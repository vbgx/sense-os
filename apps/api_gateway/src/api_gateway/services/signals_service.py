from __future__ import annotations

from sqlalchemy.orm import Session

from db.repos import signals as signals_repo
from db.models import Signal


def list_signals(*, db: Session, vertical_id: int, limit: int, offset: int):
    """
    Return signals with pagination.
    """
    rows = signals_repo.list_by_vertical(db, vertical_id=vertical_id, limit=limit, offset=offset)
    total = db.query(Signal).filter(Signal.vertical_id == int(vertical_id)).count()
    return rows, int(total)
