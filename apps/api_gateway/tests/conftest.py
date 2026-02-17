from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

TEST_DB_PATH = Path(tempfile.gettempdir()) / "sense_os_api_test.db"
TEST_DSN = f"sqlite+pysqlite:///{TEST_DB_PATH}"

from db.engine import get_engine, reset_engine  # noqa: E402
from db.models import Base  # noqa: E402
from db.uow import SqlAlchemyUnitOfWork  # noqa: E402
from db.adapters.trends import reset_trends_adapter  # noqa: E402
from api_gateway.main import app  # noqa: E402
from api_gateway.dependencies import get_uow  # noqa: E402

def _configure_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DSN)
    monkeypatch.setenv("POSTGRES_DSN", TEST_DSN)


def _build_sessionmaker():
    engine = get_engine()
    return engine, sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def _reset_schema(engine) -> None:
    """Drop and recreate all tables for a clean test state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def _ensure_test_env(monkeypatch):
    _configure_env(monkeypatch)
    reset_engine()
    reset_trends_adapter()
    yield


@pytest.fixture()
def db_session(monkeypatch):
    """Provide a clean database session for tests."""
    _configure_env(monkeypatch)
    reset_engine()
    reset_trends_adapter()
    engine, TestingSessionLocal = _build_sessionmaker()
    _reset_schema(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """FastAPI test client wired to a test database."""
    _engine, TestingSessionLocal = _build_sessionmaker()

    def _get_test_uow():
        return SqlAlchemyUnitOfWork(session_factory=TestingSessionLocal)

    app.dependency_overrides[get_uow] = _get_test_uow
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
