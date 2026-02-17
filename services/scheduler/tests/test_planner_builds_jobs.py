from __future__ import annotations

from datetime import date

from scheduler.planner import plan_vertical_run


def test_planner_builds_jobs_default_query():
    jobs = plan_vertical_run(
        vertical_id="b2b_ops",
        vertical_db_id=1,
        taxonomy_version="2026-02-17",
        source="reddit",
        run_id="r1",
        day=date(2025, 1, 1),
    )

    assert len(jobs) == 4
    ingest, process, cluster, trend = jobs

    assert ingest.queue == "ingest"
    assert ingest.query == "saas"
    assert process.queue == "process"
    assert cluster.queue == "cluster"
    assert trend.queue == "trend"
    assert trend.day == "2025-01-01"
