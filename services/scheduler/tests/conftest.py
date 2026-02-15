from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

TEST_DB_PATH = Path(tempfile.gettempdir()) / "sense_os_scheduler_test.db"

os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH}"
os.environ["POSTGRES_DSN"] = os.environ["DATABASE_URL"]

from db.engine import engine  # noqa: E402
from db.models import Base  # noqa: E402

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _reset_schema() -> None:
    """Drop and recreate all tables for a clean test state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def db_session():
    """Provide a clean database session for tests."""
    _reset_schema()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
