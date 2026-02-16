from __future__ import annotations

from typing import Generator

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
