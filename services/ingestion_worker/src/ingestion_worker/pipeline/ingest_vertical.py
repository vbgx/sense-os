from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.adapters.registry import get_adapter
from ingestion_worker.adapters.reddit.fetch import fetch_reddit_signals
from ingestion_worker.adapters.hackernews.fetch_signals import fetch_hackernews_signals
from ingestion_worker.storage.signals_writer import SignalsWriter

_CHECKPOINTS: dict[str, datetime] = {}
_CURRENT_CTX: FetchContext | None = None


def checkpoint_key(*, vertical_db_id: int, taxonomy_version: str, source: str) -> str:
    return f"{vertical_db_id}:{taxonomy_version}:{source}"


def get_checkpoint(*args, **kwargs) -> datetime | dict | None:
    if args and len(args) == 2 and not kwargs:
        _, key = args
        return _CHECKPOINTS.get(str(key))
    vertical_db_id = int(kwargs["vertical_db_id"])
    taxonomy_version = str(kwargs["taxonomy_version"])
    source = str(kwargs["source"])
    return _CHECKPOINTS.get(checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source))


def set_checkpoint(*args, **kwargs) -> None:
    if args and len(args) >= 3 and not kwargs:
        _, key, ts = args[0], args[1], args[2]
        _CHECKPOINTS[str(key)] = ts
        return
    vertical_db_id = int(kwargs["vertical_db_id"])
    taxonomy_version = str(kwargs["taxonomy_version"])
    source = str(kwargs["source"])
    ts = kwargs["ts"]
    _CHECKPOINTS[checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source)] = ts


def _checkpoint_ts(cp: datetime | dict | None) -> datetime | None:
    if cp is None:
        return None
    if isinstance(cp, datetime):
        return cp
    if isinstance(cp, dict):
        ts = cp.get("last_run_at")
        return ts if isinstance(ts, datetime) else None
    return None


def should_skip_too_recent(cp: datetime | dict | None, *, too_recent_seconds: int) -> bool:
    ts = _checkpoint_ts(cp)
    if ts is None:
        return False
    now = datetime.now(timezone.utc)
    return (now - ts) < timedelta(seconds=int(too_recent_seconds))


def _fetch_from_source(source: str, vertical_id: str):
    ctx = _CURRENT_CTX
    if ctx is None:
        raise RuntimeError("fetch context not set")

    if source == "reddit":
        return source, list(
            fetch_reddit_signals(
                vertical_id=ctx.vertical_id,
                query=ctx.query,
                limit=ctx.limit,
                vertical_db_id=ctx.vertical_db_id,
                taxonomy_version=ctx.taxonomy_version,
            )
        )
    if source == "hackernews":
        return source, list(
            fetch_hackernews_signals(
                vertical_id=ctx.vertical_id,
                query=ctx.query,
                limit=ctx.limit,
                vertical_db_id=ctx.vertical_db_id,
                taxonomy_version=ctx.taxonomy_version,
            )
        )

    adapter = get_adapter(source)
    return source, list(adapter.fetch_signals(ctx))


def _make_writer(vertical_db_id: int):
    try:
        return SignalsWriter(vertical_db_id)
    except TypeError:
        return SignalsWriter()


def _persist_with_writer(writer, signals: list[dict[str, Any]]) -> dict[str, int]:
    if hasattr(writer, "insert_many"):
        inserted, skipped = writer.insert_many(signals)
        return {"inserted": int(inserted), "skipped": int(skipped)}
    if hasattr(writer, "persist"):
        persisted = writer.persist(signals)
        return {"persisted": int(persisted)}
    if hasattr(writer, "write_signals"):
        out = writer.write_signals(signals, vertical_db_id=signals[0].get("vertical_db_id"), taxonomy_version=signals[0].get("taxonomy_version"))
        if isinstance(out, dict):
            return {k: int(v) for k, v in out.items()}
    raise AttributeError("SignalsWriter missing insert_many/persist/write_signals")


def ingest_vertical(job: dict[str, Any]) -> dict[str, int]:
    global _CURRENT_CTX
    vertical_id = str(job["vertical_id"])
    taxonomy_version = str(job.get("taxonomy_version") or "v1")
    vertical_db_id = job.get("vertical_db_id")
    if vertical_db_id is None:
        raise ValueError("job missing vertical_db_id")
    vertical_db_id = int(vertical_db_id)

    sources = job.get("sources")
    source = str(job.get("source") or "reddit")
    query = job.get("query")
    limit = int(job.get("limit") or 50)

    too_recent_seconds = int(job.get("too_recent_seconds") or 300)

    ctx = FetchContext(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        query=str(query) if query is not None else None,
        limit=limit,
    )

    writer = _make_writer(vertical_db_id)

    if sources:
        fetched = 0
        persisted = 0
        skipped_sources = 0

        _CURRENT_CTX = ctx
        try:
            for src in sources:
                key = checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=str(src))
                cp = get_checkpoint("ingest_vertical", key)
                if should_skip_too_recent(cp, too_recent_seconds=too_recent_seconds):
                    skipped_sources += 1
                    continue

                _, signals = _fetch_from_source(str(src), vertical_id)
                fetched += len(signals)
                if signals:
                    out = _persist_with_writer(writer, signals)
                    persisted += int(out.get("persisted") or out.get("inserted") or 0)

                set_checkpoint("ingest_vertical", key, datetime.now(timezone.utc))
        finally:
            _CURRENT_CTX = None

        return {"fetched": fetched, "persisted": persisted, "skipped_sources": skipped_sources}

    _CURRENT_CTX = ctx
    try:
        key = checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source)
        cp = get_checkpoint("ingest_vertical", key)
        if should_skip_too_recent(cp, too_recent_seconds=too_recent_seconds):
            return {"fetched": 0, "inserted": 0, "skipped": 1}

        _, signals = _fetch_from_source(source, vertical_id)
        fetched = len(signals)
        out = _persist_with_writer(writer, signals) if signals else {"inserted": 0, "skipped": 0}
        set_checkpoint("ingest_vertical", key, datetime.now(timezone.utc))
        return {"fetched": fetched, "inserted": int(out.get("inserted") or 0), "skipped": int(out.get("skipped") or 0)}
    finally:
        _CURRENT_CTX = None
