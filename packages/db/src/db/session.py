from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Iterator

from sqlalchemy.orm import sessionmaker

from .engine import engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


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
