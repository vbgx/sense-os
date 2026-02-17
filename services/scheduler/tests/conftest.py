from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

TEST_DB_PATH = Path(tempfile.gettempdir()) / "sense_os_scheduler_test.db"
TEST_DSN = f"sqlite+pysqlite:///{TEST_DB_PATH}"

from db.engine import get_engine, reset_engine  # noqa: E402
from db.models import Base  # noqa: E402

def _configure_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DSN)
    monkeypatch.setenv("POSTGRES_DSN", TEST_DSN)


def _build_sessionmaker():
    engine = get_engine()
    return engine, sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _reset_schema(engine) -> None:
    """Drop and recreate all tables for a clean test state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def db_session(monkeypatch):
    """Provide a clean database session for tests."""
    _configure_env(monkeypatch)
    reset_engine()
    engine, TestingSessionLocal = _build_sessionmaker()
    _reset_schema(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
