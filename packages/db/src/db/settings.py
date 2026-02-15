from __future__ import annotations

import os


def _first(*vals: str | None) -> str | None:
    for v in vals:
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


# Priority:
# 1) POSTGRES_DSN
# 2) DATABASE_URL
# 3) fallback (only for local non-docker usage)
DATABASE_URL: str = _first(
    os.getenv("POSTGRES_DSN"),
    os.getenv("DATABASE_URL"),
) or "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"


REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
