from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from ingestion_worker.pipeline.ingest_vertical import ingest_vertical


class DummyWriter:
    def __init__(self, vertical_db_id: int):
        self.vertical_db_id = vertical_db_id

    def persist(self, signals):
        return len(signals)


def _job():
    return {
        "vertical_id": "test_vertical",
        "taxonomy_version": "v1",
        "vertical_db_id": 1,
        "sources": ["github", "hackernews"],
    }


def test_skip_source_if_too_recent(monkeypatch):
    recent_ts = datetime.now(timezone.utc) - timedelta(seconds=60)

    def fake_get_checkpoint(worker: str, key: str):
        return {"last_run_at": recent_ts}

    def fake_set_checkpoint(*args, **kwargs):
        pass

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.get_checkpoint",
        fake_get_checkpoint,
    )
    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.set_checkpoint",
        fake_set_checkpoint,
    )

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical._fetch_from_source",
        lambda source, vertical_id: (source, [{"text": f"{source}-signal"}]),
    )

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.SignalsWriter",
        DummyWriter,
    )

    result = ingest_vertical(_job())

    assert result["fetched"] == 0
    assert result["persisted"] == 0
    assert result["skipped_sources"] == 2


def test_fetch_if_checkpoint_old(monkeypatch):
    old_ts = datetime.now(timezone.utc) - timedelta(hours=1)

    def fake_get_checkpoint(worker: str, key: str):
        return {"last_run_at": old_ts}

    def fake_set_checkpoint(*args, **kwargs):
        pass

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.get_checkpoint",
        fake_get_checkpoint,
    )
    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.set_checkpoint",
        fake_set_checkpoint,
    )

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical._fetch_from_source",
        lambda source, vertical_id: (source, [{"text": f"{source}-signal"}]),
    )

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.SignalsWriter",
        DummyWriter,
    )

    result = ingest_vertical(_job())

    assert result["fetched"] == 2
    assert result["persisted"] == 2
    assert result["skipped_sources"] == 0


def test_mixed_recent_and_old_sources(monkeypatch):
    now = datetime.now(timezone.utc)
    recent_ts = now - timedelta(seconds=60)
    old_ts = now - timedelta(hours=1)

    def fake_get_checkpoint(worker: str, key: str):
        if "github" in key:
            return {"last_run_at": recent_ts}
        return {"last_run_at": old_ts}

    def fake_set_checkpoint(*args, **kwargs):
        pass

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.get_checkpoint",
        fake_get_checkpoint,
    )
    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.set_checkpoint",
        fake_set_checkpoint,
    )

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical._fetch_from_source",
        lambda source, vertical_id: (source, [{"text": f"{source}-signal"}]),
    )

    monkeypatch.setattr(
        "ingestion_worker.pipeline.ingest_vertical.SignalsWriter",
        DummyWriter,
    )

    result = ingest_vertical(_job())

    assert result["fetched"] == 1
    assert result["persisted"] == 1
    assert result["skipped_sources"] == 1
