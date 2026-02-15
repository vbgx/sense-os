from __future__ import annotations

from dataclasses import asdict as _asdict
from dataclasses import dataclass
from typing import Any


def asdict(job: Any) -> dict:
    if hasattr(job, "__dataclass_fields__"):
        return _asdict(job)
    if isinstance(job, dict):
        return job
    raise TypeError(f"Unsupported job type: {type(job)!r}")


# ---------------------------------------------------------------------
# Jobs (must match planner expectations)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class IngestJob:
    type: str = "ingest_vertical"
    vertical_id: int = 0
    source: str = "reddit"
    run_id: str | None = None

    # planner may pass these (backfill / deterministic runs)
    day: str | None = None
    query: str | None = None
    limit: int | None = None
    offset: int | None = None

    queue: str = "ingest"


@dataclass(frozen=True)
class ProcessJob:
    type: str = "process_signals"
    vertical_id: int = 0
    algo_version: str = "heuristics_v1"
    run_id: str | None = None

    # planner may pass these (day-scoped processing + batch sizing / paging)
    day: str | None = None
    limit: int | None = None
    offset: int | None = None

    queue: str = "process"


@dataclass(frozen=True)
class ClusterJob:
    type: str = "cluster_vertical"
    vertical_id: int = 0
    cluster_version: str = "tfidf_v1"
    run_id: str | None = None

    # planner may pass these (day-scoped clustering + optional batching)
    day: str | None = None
    limit: int | None = None
    offset: int | None = None

    queue: str = "cluster"


@dataclass(frozen=True)
class TrendJob:
    type: str = "trend_day"
    day: str = ""  # ISO YYYY-MM-DD
    formula_version: str = "formula_v1"
    cluster_version: str = "tfidf_v1"
    run_id: str | None = None
    queue: str = "trend"


# ---------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------

def make_ingest_job(
    *,
    vertical_id: int,
    source: str,
    run_id: str | None = None,
    day: str | None = None,
    query: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> IngestJob:
    return IngestJob(
        vertical_id=vertical_id,
        source=source,
        run_id=run_id,
        day=day,
        query=query,
        limit=limit,
        offset=offset,
    )


def make_process_job(
    *,
    vertical_id: int,
    run_id: str | None = None,
    day: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> ProcessJob:
    return ProcessJob(
        vertical_id=vertical_id,
        run_id=run_id,
        day=day,
        limit=limit,
        offset=offset,
    )


def make_cluster_job(
    *,
    vertical_id: int,
    run_id: str | None = None,
    day: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> ClusterJob:
    return ClusterJob(
        vertical_id=vertical_id,
        run_id=run_id,
        day=day,
        limit=limit,
        offset=offset,
    )


def make_trend_job(*, day: str, run_id: str | None = None) -> TrendJob:
    return TrendJob(day=day, run_id=run_id)


# ---------------------------------------------------------------------
# Backward-compatible aliases
# ---------------------------------------------------------------------

def make_ingest_vertical_job(
    *,
    vertical_id: int,
    source: str,
    run_id: str | None = None,
    day: str | None = None,
    query: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> IngestJob:
    return make_ingest_job(
        vertical_id=vertical_id,
        source=source,
        run_id=run_id,
        day=day,
        query=query,
        limit=limit,
        offset=offset,
    )


def make_process_signals_job(
    *,
    vertical_id: int,
    run_id: str | None = None,
    day: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> ProcessJob:
    return make_process_job(
        vertical_id=vertical_id,
        run_id=run_id,
        day=day,
        limit=limit,
        offset=offset,
    )


def make_cluster_vertical_job(
    *,
    vertical_id: int,
    run_id: str | None = None,
    day: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> ClusterJob:
    return make_cluster_job(
        vertical_id=vertical_id,
        run_id=run_id,
        day=day,
        limit=limit,
        offset=offset,
    )


def make_trend_day_job(*, day: str, run_id: str | None = None) -> TrendJob:
    return make_trend_job(day=day, run_id=run_id)
