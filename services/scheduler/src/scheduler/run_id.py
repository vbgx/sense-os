from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4


def new_run_id(day: date | None = None) -> str:
    """
    run_id is used for observability and idempotency keys.

    For backfill/nightly:
      - include the logical day so logs/metrics correlate cleanly
      - keep a uuid suffix so multiple attempts are distinguishable while still traceable
    """
    if day is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"run_{ts}_{uuid4().hex[:8]}"
    return f"run_{day.isoformat()}_{uuid4().hex[:8]}"
