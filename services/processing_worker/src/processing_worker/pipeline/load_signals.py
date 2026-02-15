from db.session import SessionLocal
from db.repos import signals as signals_repo


def load_batch(vertical_id: int, limit: int, offset: int):
    db = SessionLocal()
    try:
        return signals_repo.list_by_vertical(
            db,
            vertical_id=vertical_id,
            limit=limit,
            offset=offset,
        )
    finally:
        db.close()
