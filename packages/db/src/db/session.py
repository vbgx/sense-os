from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Iterator

from sqlalchemy.orm import sessionmaker

from .engine import get_engine

_session_factory = None
_session_factory_dsn: str | None = None


def _get_sessionmaker():
    global _session_factory, _session_factory_dsn
    engine = get_engine()
    dsn = str(engine.url)
    if _session_factory is None or _session_factory_dsn != dsn:
        _session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False,
        )
        _session_factory_dsn = dsn
    return _session_factory


def SessionLocal():
    return _get_sessionmaker()()


def get_session() -> Generator:
    """
    FastAPI dependency.
    Yields a DB session and guarantees close.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator:
    """
    Context manager for short-lived DB sessions with commit/rollback handling.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
