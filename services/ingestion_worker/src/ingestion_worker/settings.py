from __future__ import annotations

import os


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return bool(default)
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None:
        return int(default)
    try:
        return int(v)
    except Exception:
        return int(default)


# Fanout / ingestion controls
INGEST_FAIL_FAST: bool = _env_bool("INGEST_FAIL_FAST", False)
INGEST_FANOUT_MAX_WORKERS: int = _env_int("INGEST_FANOUT_MAX_WORKERS", 8)
INGEST_MAX_SIGNALS_PER_SOURCE: int = _env_int("INGEST_MAX_SIGNALS_PER_SOURCE", 200)
