from db.init_db import init_db
from db.session import SessionLocal
from db.repos import verticals as vertical_repo


def ensure_vertical(name: str) -> int:
    init_db()
    db = SessionLocal()
    try:
        v = vertical_repo.get_by_name(db, name)
        if v is None:
            v = vertical_repo.create(db, name=name)
        return int(v.id)
    finally:
        db.close()
