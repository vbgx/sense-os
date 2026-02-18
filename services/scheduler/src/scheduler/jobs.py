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


@dataclass(frozen=True)
class IngestJob:
    type: str = "ingest_vertical"
    vertical_id: str = ""
    vertical_db_id: int = 0
    taxonomy_version: str = ""

    # legacy single-source path (kept for backward compatibility)
    source: str = "reddit"

    # multi-source path
    sources: list[str] | None = None

    run_id: str | None = None

    day: str | None = None
    start_day: str | None = None
    end_day: str | None = None

    query: str | None = None
    limit: int | None = None
    offset: int | None = None

    queue: str = "ingest"


@dataclass(frozen=True)
class ProcessJob:
    type: str = "process_signals"
    vertical_id: str = ""
    vertical_db_id: int = 0
    taxonomy_version: str = ""
    algo_version: str = "heuristics_v1"
    run_id: str | None = None

    day: str | None = None
    limit: int | None = None
    offset: int | None = None

    queue: str = "process"


@dataclass(frozen=True)
class ClusterJob:
    type: str = "cluster_vertical"
    vertical_id: str = ""
    vertical_db_id: int = 0
    taxonomy_version: str = ""
    cluster_version: str = "tfidf_v1"
    run_id: str | None = None

    day: str | None = None
    limit: int | None = None
    offset: int | None = None

    queue: str = "cluster"


@dataclass(frozen=True)
class TrendJob:
    type: str = "trend_day"
    vertical_id: str = ""
    vertical_db_id: int = 0
    taxonomy_version: str = ""
    day: str = ""
    formula_version: str = "formula_v1"
    cluster_version: str = "tfidf_v1"
    run_id: str | None = None
    queue: str = "trend"
