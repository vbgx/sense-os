from __future__ import annotations

from datetime import date
from typing import List, Optional

from scheduler.jobs import ClusterJob, IngestJob, ProcessJob, TrendJob


def plan_vertical_run(
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    source: str,
    run_id: str,
    day: Optional[date] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[object]:
    day_s = day.isoformat() if day else None
    start_day_s = day_s
    end_day_s = day_s

    if query is None and source == "reddit":
        query = "saas"

    ingest = IngestJob(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        source=source,
        run_id=run_id,
        day=day_s,
        start_day=start_day_s,
        end_day=end_day_s,
        query=query,
        limit=limit if limit is not None else (80 if source == "reddit" else None),
        offset=offset,
    )

    process = ProcessJob(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        run_id=run_id,
        day=day_s,
        limit=limit,
        offset=offset,
    )

    cluster = ClusterJob(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        cluster_version="tfidf_v1",
        run_id=run_id,
        day=day_s,
        limit=limit,
        offset=offset,
    )

    trend = TrendJob(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        day=day_s or "",
        formula_version="formula_v1",
        cluster_version="tfidf_v1",
        run_id=run_id,
    )

    return [ingest, process, cluster, trend]
