from __future__ import annotations

from datetime import date
from typing import List, Optional

from scheduler.jobs import ClusterJob, IngestJob, ProcessJob, TrendJob


def _list_available_sources() -> list[str]:
    """
    Sources are owned by ingestion_worker.adapters.registry.

    Registry is best-effort: only adapters that import cleanly appear here.
    """
    try:
        from ingestion_worker.adapters.registry import list_sources  # type: ignore
    except Exception:
        return ["reddit"]

    try:
        out = list_sources()
        xs = [str(x).strip() for x in out if str(x).strip()]
        return xs or ["reddit"]
    except Exception:
        return ["reddit"]


def _dedup_keep_order(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        s = str(x).strip()
        if not s:
            continue
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


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
    sources: Optional[list[str]] = None,
) -> List[object]:
    day_s = day.isoformat() if day else None
    start_day_s = day_s
    end_day_s = day_s

    src_norm = str(source).strip().lower()
    multi = src_norm in {"multi", "all", "*"}

    job_sources: list[str] | None = None

    if multi:
        # Use explicit sources if provided (from config/verticals/*.json),
        # otherwise fallback to "all adapters that import cleanly".
        if sources is not None:
            job_sources = _dedup_keep_order([str(s) for s in sources])
        else:
            job_sources = _dedup_keep_order(_list_available_sources())

        # HARD GUARD: never allow empty sources in multi-mode
        if not job_sources:
            job_sources = ["reddit"]

        # keep previous behavior: if caller didn't pick a query, default one
        if query is None:
            query = "saas"
        if limit is None:
            limit = 80
    else:
        # legacy single-source behavior
        if query is None and src_norm == "reddit":
            query = "saas"
        if limit is None and src_norm == "reddit":
            limit = 80

    ingest = IngestJob(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        source=source,              # keep original for backward-compat
        sources=job_sources,        # the important part for multi-mode
        run_id=run_id,
        day=day_s,
        start_day=start_day_s,
        end_day=end_day_s,
        query=query,
        limit=limit,
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
