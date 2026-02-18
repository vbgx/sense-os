from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.adapters.registry import get_adapter
from ingestion_worker.adapters.reddit.fetch import fetch_reddit_signals
from ingestion_worker.adapters.hackernews.fetch_signals import fetch_hackernews_signals

_CHECKPOINTS: dict[str, datetime] = {}


def checkpoint_key(*, vertical_db_id: int, taxonomy_version: str, source: str) -> str:
    return f"{vertical_db_id}:{taxonomy_version}:{source}"


def get_checkpoint(*, vertical_db_id: int, taxonomy_version: str, source: str) -> datetime | None:
    return _CHECKPOINTS.get(checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source))


def set_checkpoint(*, vertical_db_id: int, taxonomy_version: str, source: str, ts: datetime) -> None:
    _CHECKPOINTS[checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source)] = ts


def should_skip_too_recent(cp: datetime | None, *, too_recent_seconds: int) -> bool:
    if cp is None:
        return False
    now = datetime.now(timezone.utc)
    return (now - cp) < timedelta(seconds=int(too_recent_seconds))


def ingest_vertical(job: dict[str, Any]) -> dict[str, int]:
    vertical_id = str(job["vertical_id"])
    taxonomy_version = str(job.get("taxonomy_version") or "v1")
    vertical_db_id = job.get("vertical_db_id")
    if vertical_db_id is None:
        raise ValueError("job missing vertical_db_id")
    vertical_db_id = int(vertical_db_id)

    source = str(job.get("source") or "reddit")
    query = job.get("query")
    limit = int(job.get("limit") or 50)

    too_recent_seconds = int(job.get("too_recent_seconds") or 0)
    cp = get_checkpoint(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source)
    if too_recent_seconds > 0 and should_skip_too_recent(cp, too_recent_seconds=too_recent_seconds):
        return {"fetched": 0, "skipped": 1}

    ctx = FetchContext(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        query=str(query) if query is not None else None,
        limit=limit,
    )

    if source == "reddit":
        _ = list(fetch_reddit_signals(vertical_id=ctx.vertical_id, query=ctx.query, limit=ctx.limit, vertical_db_id=ctx.vertical_db_id, taxonomy_version=ctx.taxonomy_version))
    elif source == "hackernews":
        _ = list(fetch_hackernews_signals(vertical_id=ctx.vertical_id, query=ctx.query, limit=ctx.limit, vertical_db_id=ctx.vertical_db_id, taxonomy_version=ctx.taxonomy_version))
    else:
        adapter = get_adapter(source)
        _ = list(adapter.fetch_signals(ctx))

    set_checkpoint(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source, ts=datetime.now(timezone.utc))
    return {"fetched": limit, "skipped": 0}
