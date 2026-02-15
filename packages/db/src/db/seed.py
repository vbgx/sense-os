from db.init_db import init_db
from db.session import SessionLocal
from db.repos import verticals as vertical_repo


DEFAULT_VERTICALS = [
    "default",
]


def seed_verticals(names=DEFAULT_VERTICALS) -> int:
    init_db()
    db = SessionLocal()
    created = 0
    try:
        for name in names:
            existing = vertical_repo.get_by_name(db, name)
            if existing is None:
                vertical_repo.create(db, name)
                created += 1
        return created
    finally:
        db.close()


if __name__ == "__main__":
    n = seed_verticals()
    print(f"seeded_verticals_created={n}")
