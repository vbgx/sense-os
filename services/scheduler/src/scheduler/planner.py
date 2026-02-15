from __future__ import annotations

from datetime import date
from typing import Optional, List

from scheduler.jobs import IngestJob, ProcessJob, ClusterJob, TrendJob


def plan_vertical_run(
    vertical_id: int,
    source: str,
    run_id: str,
    day: Optional[date] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[object]:
    day_s = day.isoformat() if day else None

    if query is None and source == "reddit":
        query = "saas"

    ingest = IngestJob(
        vertical_id=vertical_id,
        source=source,
        run_id=run_id,
        day=day_s,
        query=query,
        limit=limit if limit is not None else (80 if source == "reddit" else None),
        offset=offset,
    )

    process = ProcessJob(
        vertical_id=vertical_id,
        run_id=run_id,
        day=day_s,
        limit=limit,
        offset=offset,
    )

    cluster = ClusterJob(
        vertical_id=vertical_id,
        cluster_version="tfidf_v1",
        run_id=run_id,
        day=day_s,
        limit=limit,
        offset=offset,
    )

    trend = TrendJob(
        day=day_s or "",
        formula_version="formula_v1",
        cluster_version="tfidf_v1",
        run_id=run_id,
    )

    return [ingest, process, cluster, trend]
