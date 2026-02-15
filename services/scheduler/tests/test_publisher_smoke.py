from __future__ import annotations

from scheduler.jobs import IngestJob, ProcessJob
from scheduler.publisher import publish_jobs


class DummyClient:
    published = []

    def __init__(self, *args, **kwargs) -> None:
        pass

    def publish(self, queue, payload):
        DummyClient.published.append((queue, payload))


def test_publisher_publishes_jobs(monkeypatch):
    DummyClient.published = []
    monkeypatch.setattr("scheduler.publisher.RedisJobQueueClient", DummyClient)

    jobs = [
        IngestJob(vertical_id=1, source="reddit", run_id="r1"),
        ProcessJob(vertical_id=1, run_id="r1"),
    ]
    n = publish_jobs(jobs)

    assert n == 2
    queues = [q for q, _ in DummyClient.published]
    assert queues == ["ingest", "process"]
