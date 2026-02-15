import time
from sqlalchemy.exc import OperationalError

from db.engine import engine
from db.models import Base


def init_db(max_wait_s: int = 30, sleep_s: float = 1.0) -> None:
    """
    Initialize DB schema (V0) with a retry loop so container startup is robust.

    Postgres can be "started" at docker level but still refuse connections
    for a few seconds. We wait until connection succeeds.
    """
    deadline = time.time() + max_wait_s
    last_err: Exception | None = None

    while time.time() < deadline:
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as e:
            last_err = e
            time.sleep(sleep_s)

    raise RuntimeError(f"DB init failed after {max_wait_s}s: {last_err}")
