from __future__ import annotations

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable

from ingestion_worker.settings import (
    INGEST_FAIL_FAST,
    INGEST_FANOUT_MAX_WORKERS,
    INGEST_MAX_SIGNALS_PER_SOURCE,
)

log = logging.getLogger(__name__)


def _norm_text(t: str) -> str:
    return " ".join((t or "").strip().split()).lower()


def _stable_key(source: str, item: dict[str, Any]) -> str:
    """
    Best-effort dedup key across sources.
    Preference order:
      1) source + external_id (or source_id)
      2) hash(text + created_at_day)
    """
    ext = item.get("external_id") or item.get("source_external_id") or item.get("source_id")
    if isinstance(ext, str) and ext.strip():
        return f"{source}::ext::{ext.strip()}"

    text = _norm_text(str(item.get("text") or item.get("content") or item.get("title") or ""))
    created_at = item.get("created_at")
    day = ""
    if isinstance(created_at, datetime):
        day = created_at.date().isoformat()
    elif isinstance(created_at, str) and created_at:
        day = created_at[:10]

    raw = f"{source}::{day}::{text}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{source}::h::{h}"


def dedup_signals(items: Iterable[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source, item in items:
        k = _stable_key(source, item)
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


@dataclass(frozen=True)
class FanoutResult:
    source: str
    items: list[dict[str, Any]]
    error: str | None = None


def fanout_fetch(
    *,
    sources: list[str],
    fetch_fn: Callable[[str], list[dict[str, Any]]],
    max_workers: int | None = None,
) -> list[FanoutResult]:
    """
    Run fetch_fn(source) in parallel across sources.
    """
    if max_workers is None:
        max_workers = int(INGEST_FANOUT_MAX_WORKERS)

    results: list[FanoutResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(fetch_fn, src): src for src in sources}

        for fut in as_completed(futs):
            src = futs[fut]
            try:
                items = fut.result()
                if not isinstance(items, list):
                    items = []
                if len(items) > int(INGEST_MAX_SIGNALS_PER_SOURCE):
                    items = items[: int(INGEST_MAX_SIGNALS_PER_SOURCE)]
                results.append(FanoutResult(source=src, items=items, error=None))
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                log.warning("fanout source failed source=%s err=%s", src, msg)
                results.append(FanoutResult(source=src, items=[], error=msg))
                if bool(INGEST_FAIL_FAST):
                    raise

    return results
