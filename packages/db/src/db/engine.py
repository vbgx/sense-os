from __future__ import annotations

import os

from sqlalchemy import create_engine

from db.settings import DATABASE_URL

_engine = None
_engine_dsn: str | None = None


def get_engine():
    global _engine, _engine_dsn
    dsn = os.getenv("DATABASE_URL") or DATABASE_URL
    if _engine is None or _engine_dsn != dsn:
        _engine = create_engine(dsn, pool_pre_ping=True)
        _engine_dsn = dsn
    return _engine


def reset_engine() -> None:
    global _engine, _engine_dsn
    if _engine is not None:
        try:
            _engine.dispose()
        except Exception:
            pass
    _engine = None
    _engine_dsn = None


class _EngineProxy:
    def __getattr__(self, name):
        return getattr(get_engine(), name)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<EngineProxy dsn={_engine_dsn!r}>"


# Lazy proxy to avoid import-time engine creation.
engine = _EngineProxy()
