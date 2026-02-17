from __future__ import annotations

from sense_queue.worker_base import handle_job

from ingestion_worker import main as worker_main


def test_worker_consumes_ingest_job(monkeypatch):
    called = {}

    def fake_ingest(job):
        called["job"] = job
        return {"fetched": 1, "inserted": 1, "skipped": 0}

    monkeypatch.setattr(worker_main, "ingest_vertical", fake_ingest)

    job = {
        "type": "ingest_vertical",
        "vertical_id": "b2b_ops",
        "vertical_db_id": 1,
        "taxonomy_version": "2026-02-17",
        "source": "reddit",
        "run_id": "r1",
    }
    assert handle_job(job) is True
    assert called["job"]["vertical_id"] == "b2b_ops"
