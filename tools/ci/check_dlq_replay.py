from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import sessionmaker

from db.engine import engine
from db.models import Signal
from db.repos import signals as signals_repo
from db.repos import verticals as verticals_repo
from sense_queue.client import RedisJobQueueClient
from sense_queue.retry import RetryPolicy
from sense_queue import worker_base


SessionLocal = sessionmaker(bind=engine)


def _require_postgres() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("check_dlq_replay requires Postgres")


def _run_once(client: RedisJobQueueClient, queue: str) -> None:
    client._drain_retry_queue(queue)
    item = client.r.blpop(queue, timeout=2)
    if not item:
        raise AssertionError("expected job in queue")
    _key, raw = item
    try:
        job = json.loads(raw)
    except Exception as exc:
        raise AssertionError(f"invalid job payload: {raw}") from exc

    try:
        worker_base.handle_job(job)
    except Exception as exc:
        client._schedule_retry(queue, job, exc)


def main() -> None:
    _require_postgres()

    worker_base.HANDLERS.clear()

    job_type = "ci_dlq_test"
    queue = f"ci-dlq-{uuid.uuid4().hex}"
    vertical_name = f"ci-vertical-{uuid.uuid4().hex}"
    external_id = f"ext-{uuid.uuid4().hex}"

    @worker_base.job_handler(job_type)
    def _handler(job: dict) -> None:
        db = SessionLocal()
        try:
            vertical = verticals_repo.get_by_name(db, vertical_name)
            if vertical is None:
                vertical = verticals_repo.create(db, vertical_name)
            _row, _created = signals_repo.create_if_absent(
                db,
                vertical_db_id=vertical.id,
                vertical_id=vertical.name,
                source="ci",
                external_id=external_id,
                content="ci payload",
                url=None,
            )
            db.commit()
            attempt = int(job.get("_attempt", 0))
            if job.get("fail_after_write") and attempt == 0:
                raise RuntimeError("boom")
        finally:
            db.close()

    client = RedisJobQueueClient(retry_policy=RetryPolicy(max_retries=0))
    dlq_key = client._dlq_key(queue)
    retry_key = client._retry_key(queue)

    client.r.delete(queue, dlq_key, retry_key)

    job = {
        "type": job_type,
        "vertical_id": None,
        "vertical_db_id": None,
        "taxonomy_version": None,
        "day": None,
        "source": "ci",
        "run_id": None,
        "fail_after_write": True,
    }

    client.publish(queue, job)
    _run_once(client, queue)

    if client.r.llen(dlq_key) != 1:
        raise AssertionError("expected job in DLQ after failure")

    db = SessionLocal()
    try:
        count_after_fail = (
            db.query(Signal)
            .filter(Signal.source == "ci")
            .filter(Signal.external_id == external_id)
            .count()
        )
    finally:
        db.close()

    if count_after_fail != 1:
        raise AssertionError(f"expected 1 signal after failure, got {count_after_fail}")

    raw = client.r.lpop(dlq_key)
    if not raw:
        raise AssertionError("expected DLQ item for replay")
    client.r.rpush(queue, raw)

    _run_once(client, queue)

    if client.r.llen(dlq_key) != 0:
        raise AssertionError("expected DLQ empty after replay")

    db = SessionLocal()
    try:
        count_after_replay = (
            db.query(Signal)
            .filter(Signal.source == "ci")
            .filter(Signal.external_id == external_id)
            .count()
        )
    finally:
        db.close()

    if count_after_replay != 1:
        raise AssertionError(
            f"expected 1 signal after replay, got {count_after_replay}"
        )

    print("OK: DLQ replay idempotency")


if __name__ == "__main__":
    main()
