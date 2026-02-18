from __future__ import annotations

from db.session import SessionLocal
from db.repos import signals as signals_repo


def load_batch(vertical_db_id: int, limit: int, offset: int):
    db = SessionLocal()
    try:
        return signals_repo.list_by_vertical_db_id(
            db,
            vertical_db_id=vertical_db_id,
            limit=limit,
            offset=offset,
        )
    finally:
        db.close()
