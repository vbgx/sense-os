import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from db.engine import get_engine


def init_db(max_wait_s: int = 30, sleep_s: float = 1.0) -> None:
    """
    Wait for DB connectivity only.

    Schema creation is handled by Alembic migrations.
    """
    deadline = time.time() + max_wait_s
    last_err: Exception | None = None

    while time.time() < deadline:
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError as e:
            last_err = e
            time.sleep(sleep_s)

    raise RuntimeError(f"DB init failed after {max_wait_s}s: {last_err}")
