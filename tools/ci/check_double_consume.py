from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import sessionmaker

from db.engine import engine
from db.models import Signal
from db.repos import signals as signals_repo
from db.repos import verticals as verticals_repo


SessionLocal = sessionmaker(bind=engine)


def _require_postgres() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("check_double_consume requires Postgres")


def main() -> None:
    _require_postgres()

    vertical_name = f"ci-vertical-{uuid.uuid4().hex}"
    source = "ci"
    external_id = f"ext-{uuid.uuid4().hex}"

    db = SessionLocal()
    try:
        vertical = verticals_repo.create(db, vertical_name)
    finally:
        db.close()

    barrier = threading.Barrier(2)

    def _task() -> bool:
        db_local = SessionLocal()
        try:
            barrier.wait(timeout=10)
            _row, created = signals_repo.create_if_absent(
                db_local,
                vertical_id=vertical.id,
                source=source,
                external_id=external_id,
                content="ci payload",
                url=None,
            )
            db_local.commit()
            return bool(created)
        finally:
            db_local.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        created_flags = [executor.submit(_task).result(timeout=10) for _ in range(2)]

    if sum(1 for flag in created_flags if flag) != 1:
        raise AssertionError(f"expected one create, got flags={created_flags}")

    db = SessionLocal()
    try:
        count = (
            db.query(Signal)
            .filter(Signal.source == source)
            .filter(Signal.external_id == external_id)
            .count()
        )
    finally:
        db.close()

    if count != 1:
        raise AssertionError(f"expected 1 signal row, got {count}")

    print("OK: double-consume idempotency")


if __name__ == "__main__":
    main()
