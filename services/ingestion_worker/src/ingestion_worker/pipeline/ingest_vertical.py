from __future__ import annotations

import hashlib
import logging
import os
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.adapters.hackernews.fetch_signals import fetch_hackernews_signals
from ingestion_worker.adapters.reddit.fetch import fetch_reddit_signals
from ingestion_worker.adapters.registry import get_adapter
from ingestion_worker.storage.signals_writer import SignalsWriter

log = logging.getLogger(__name__)

_CHECKPOINTS: dict[str, datetime] = {}
_CURRENT_CTX: FetchContext | None = None

# 🔥 HARD SKIP (temporary): Reddit disabled no matter what.
_HARD_DISABLED_SOURCES = {"reddit"}

# ✅ If registry/config yields nothing usable, we still want the system to run.
# Add any other adapters you *know* exist locally.
_FALLBACK_SOURCES = ["hackernews"]


def checkpoint_key(*, vertical_db_id: int, taxonomy_version: str, source: str) -> str:
    return f"{vertical_db_id}:{taxonomy_version}:{source}"


def get_checkpoint(*args, **kwargs) -> datetime | dict | None:
    # legacy signature: get_checkpoint(name, key)
    if args and len(args) == 2 and not kwargs:
        _, key = args
        return _CHECKPOINTS.get(str(key))
    vertical_db_id = int(kwargs["vertical_db_id"])
    taxonomy_version = str(kwargs["taxonomy_version"])
    source = str(kwargs["source"])
    return _CHECKPOINTS.get(
        checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source)
    )


def set_checkpoint(*args, **kwargs) -> None:
    """
    Store a datetime checkpoint.

    Supports both:
      - legacy: set_checkpoint(name, key, ts_datetime)
      - named:  set_checkpoint(vertical_db_id=..., taxonomy_version=..., source=..., ts=datetime)
    """
    # legacy signature: set_checkpoint(name, key, ts)
    if args and len(args) >= 3 and not kwargs:
        _, key, ts = args[0], args[1], args[2]
        if isinstance(ts, datetime):
            _CHECKPOINTS[str(key)] = ts
        else:
            # don't poison state
            _CHECKPOINTS[str(key)] = datetime.now(timezone.utc)
        return

    vertical_db_id = int(kwargs["vertical_db_id"])
    taxonomy_version = str(kwargs["taxonomy_version"])
    source = str(kwargs["source"])
    ts = kwargs.get("ts")
    if not isinstance(ts, datetime):
        ts = datetime.now(timezone.utc)
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


def _as_list(x: Any) -> list[dict[str, Any]]:
    if x is None:
        return []
    if isinstance(x, list):
        return [it for it in x if isinstance(it, dict)]
    try:
        return [it for it in list(x) if isinstance(it, dict)]
    except Exception:
        return []


def _canon_str(x: Any) -> str | None:
    if x is None:
        return None
    s = str(x).strip()
    return s if s else None


def _norm_text(t: str) -> str:
    return " ".join((t or "").strip().split()).lower()


def _infer_day_str(item: dict[str, Any]) -> str:
    created_at = item.get("created_at")
    if isinstance(created_at, datetime):
        return created_at.date().isoformat()
    if isinstance(created_at, str) and created_at:
        return created_at[:10]
    return ""


def _stable_external_id(*, source: str, item: dict[str, Any]) -> str:
    url = item.get("url") or item.get("link") or item.get("permalink")
    if isinstance(url, str) and url.strip():
        raw = f"{source}::url::{url.strip()}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    text = item.get("content") or item.get("text") or item.get("title") or item.get("body") or ""
    text_s = _norm_text(str(text))
    day = _infer_day_str(item)
    raw = f"{source}::t::{day}::{text_s}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _coerce_created_at(item: dict[str, Any]) -> datetime | None:
    v = item.get("created_at")
    if isinstance(v, datetime):
        return v
    if isinstance(v, str) and v.strip():
        s = v.strip()
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s)
        except Exception:
            return None
    for k in ("published_at", "timestamp", "time", "date"):
        v2 = item.get(k)
        if isinstance(v2, datetime):
            return v2
        if isinstance(v2, str) and v2.strip():
            s = v2.strip()
            try:
                if s.endswith("Z"):
                    s = s[:-1] + "+00:00"
                return datetime.fromisoformat(s)
            except Exception:
                continue
    return None


def _pick_content(item: dict[str, Any]) -> str | None:
    for k in ("content", "text", "body", "description", "summary", "title"):
        v = item.get(k)
        s = _canon_str(v)
        if s:
            return s
    return None


def _pick_title(item: dict[str, Any]) -> str | None:
    for k in ("title", "headline", "name"):
        s = _canon_str(item.get(k))
        if s:
            return s
    return None


def _pick_url(item: dict[str, Any]) -> str | None:
    for k in ("url", "link", "permalink"):
        s = _canon_str(item.get(k))
        if s:
            return s
    return None


def _enrich_signal(item: dict[str, Any], *, ctx: FetchContext, source: str) -> dict[str, Any] | None:
    out = dict(item)

    out["vertical_id"] = ctx.vertical_id
    out["taxonomy_version"] = ctx.taxonomy_version
    out["vertical_db_id"] = ctx.vertical_db_id
    out["source"] = str(source)

    content = _pick_content(out)
    if not content:
        return None
    out["content"] = content

    title = _pick_title(out)
    if title:
        out.setdefault("title", title)

    url = _pick_url(out)
    if url:
        out.setdefault("url", url)

    created_at = _coerce_created_at(out)
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    out["created_at"] = created_at

    ext = _canon_str(out.get("external_id"))
    if not ext:
        for k in ("source_external_id", "source_id", "id", "item_id"):
            v = _canon_str(out.get(k))
            if v:
                out["external_id"] = v
                break
    ext2 = _canon_str(out.get("external_id"))
    if not ext2:
        out["external_id"] = _stable_external_id(source=str(source), item=out)

    return out


def _disabled_sources() -> set[str]:
    raw = str(os.environ.get("INGESTION_DISABLE_SOURCES", "")).strip()
    disabled = set(_HARD_DISABLED_SOURCES)
    if raw:
        parts = [p.strip().lower() for p in raw.split(",")]
        disabled |= {p for p in parts if p}
    return disabled


def _filter_sources(sources: list[str]) -> list[str]:
    disabled = _disabled_sources()
    return [s for s in sources if str(s).strip().lower() not in disabled]


def _fetch_from_source(source: str, vertical_id: str):
    ctx = _CURRENT_CTX
    if ctx is None:
        raise RuntimeError("fetch context not set")

    src_norm = str(source).strip().lower()
    if src_norm in _disabled_sources():
        raise RuntimeError(f"source disabled: {source}")

    if src_norm == "reddit":
        return source, _as_list(
            fetch_reddit_signals(
                vertical_id=ctx.vertical_id,
                query=ctx.query,
                limit=ctx.limit,
                vertical_db_id=ctx.vertical_db_id,
                taxonomy_version=ctx.taxonomy_version,
            )
        )

    if src_norm == "hackernews":
        return source, _as_list(
            fetch_hackernews_signals(
                vertical_id=ctx.vertical_id,
                query=ctx.query,
                limit=ctx.limit,
                vertical_db_id=ctx.vertical_db_id,
                taxonomy_version=ctx.taxonomy_version,
            )
        )

    adapter = get_adapter(source)
    if hasattr(adapter, "fetch_signals"):
        return source, _as_list(adapter.fetch_signals(ctx))
    if hasattr(adapter, "fetch"):
        return source, _as_list(adapter.fetch(ctx))
    raise AttributeError(f"adapter missing fetch/fetch_signals: {adapter!r}")


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
        out = writer.write_signals(
            signals,
            vertical_db_id=signals[0].get("vertical_db_id"),
            taxonomy_version=signals[0].get("taxonomy_version"),
        )
        if isinstance(out, dict):
            return {k: int(v) for k, v in out.items()}
    raise AttributeError("SignalsWriter missing insert_many/persist/write_signals")


def _safe_sources_from_registry() -> list[str]:
    # ⚠️ Your current registry seems to return only reddit -> after filter it's empty.
    # So: try registry, then fallback hardcoded.
    try:
        from ingestion_worker.adapters.registry import list_sources  # type: ignore

        out = [str(x).strip() for x in list_sources() if str(x).strip()]
        out = _filter_sources(out)
        if out:
            return out
    except Exception:
        pass

    # guaranteed fallback
    return _filter_sources(list(_FALLBACK_SOURCES))


def ingest_vertical(job: dict[str, Any]) -> dict[str, int]:
    global _CURRENT_CTX

    t0 = time.perf_counter()

    vertical_id = str(job.get("vertical_id") or "")
    taxonomy_version = str(job.get("taxonomy_version") or "v1")
    vertical_db_id = job.get("vertical_db_id")
    source = str(job.get("source") or "reddit")
    sources = job.get("sources")
    query = job.get("query")
    limit = int(job.get("limit") or 50)

    if not vertical_id:
        raise ValueError("job missing vertical_id")
    if vertical_db_id is None:
        raise ValueError("job missing vertical_db_id")
    vertical_db_id = int(vertical_db_id)

    too_recent_seconds = int(job.get("too_recent_seconds") or 300)

    ctx = FetchContext(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        query=str(query) if query is not None else None,
        limit=limit,
    )

    writer = _make_writer(vertical_db_id)

    # ---- MULTI coercion ----
    multi = source.strip().lower() in {"multi", "all", "*"}
    if multi and not sources:
        sources = _safe_sources_from_registry()
        log.warning("ingest_multi_sources_missing_fallback fallback_sources=%s", sources)

    # apply disable filter (multi and single)
    if sources:
        norm_sources: list[str] = []
        for s in sources if isinstance(sources, list) else list(sources):
            ss = str(s).strip()
            if ss:
                norm_sources.append(ss)

        norm_sources = _filter_sources(norm_sources)

        # If config list becomes empty (ex: only reddit), fallback to registry/hard list
        if not norm_sources:
            fallback = _safe_sources_from_registry()
            if not fallback:
                log.warning("ingest_all_sources_disabled disabled=%s", sorted(_disabled_sources()))
                return {
                    "fetched": 0,
                    "inserted": 0,
                    "skipped_db": 0,
                    "skipped_sources": 0,
                    "failed_sources": 0,
                    "skipped_items": 0,
                }
            norm_sources = fallback
            log.warning("ingest_sources_fallback_to_registry sources=%s", norm_sources)

        # 🎲 MULTI strategy: pick ONE source randomly (seeded) to avoid blasting providers.
        seed = f"{vertical_db_id}:{taxonomy_version}:{vertical_id}:{job.get('day')}:{query}:{limit}"
        rng = random.Random(seed)
        src = rng.choice(norm_sources)

        log.info("ingest_multi_pick source=%s candidates=%s", src, norm_sources)

        key = checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=src)
        cp = get_checkpoint("ingest_vertical", key)
        if should_skip_too_recent(cp, too_recent_seconds=too_recent_seconds):
            log.info("ingest_source_skipped_too_recent source=%s", src)
            return {"fetched": 0, "inserted": 0, "skipped_db": 0, "skipped_sources": 1, "failed_sources": 0, "skipped_items": 0}

        _CURRENT_CTX = ctx
        try:
            try:
                _, raw = _fetch_from_source(src, vertical_id)
            except Exception as e:
                log.warning("ingest_source_failed source=%s err=%s:%s", src, type(e).__name__, str(e))
                set_checkpoint("ingest_vertical", key, datetime.now(timezone.utc))
                return {"fetched": 0, "inserted": 0, "skipped_db": 0, "skipped_sources": 0, "failed_sources": 1, "skipped_items": 0}

            enriched: list[dict[str, Any]] = []
            skipped_items = 0
            for it in raw:
                e = _enrich_signal(it, ctx=ctx, source=src)
                if e is None:
                    skipped_items += 1
                    continue
                enriched.append(e)

            fetched = len(enriched)
            inserted_total = 0
            skipped_db_total = 0

            if enriched:
                out = _persist_with_writer(writer, enriched)
                inserted_total = int(out.get("inserted") or out.get("persisted") or 0)
                skipped_db_total = int(out.get("skipped") or 0)

            set_checkpoint("ingest_vertical", key, datetime.now(timezone.utc))
        finally:
            _CURRENT_CTX = None

        log.info(
            "ingest_done mode=multi_random source=%s fetched=%s inserted=%s skipped_db=%s skipped_items=%s seconds=%.3f",
            src,
            fetched,
            inserted_total,
            skipped_db_total,
            skipped_items,
            time.perf_counter() - t0,
        )
        return {
            "fetched": fetched,
            "inserted": inserted_total,
            "skipped_db": skipped_db_total,
            "skipped_sources": 0,
            "failed_sources": 0,
            "skipped_items": skipped_items,
        }

    # ---- single source path ----
    if source.strip().lower() in _disabled_sources():
        log.warning("ingest_single_source_disabled source=%s disabled=%s", source, sorted(_disabled_sources()))
        return {"fetched": 0, "inserted": 0, "skipped": 1}

    _CURRENT_CTX = ctx
    try:
        key = checkpoint_key(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version, source=source)
        cp = get_checkpoint("ingest_vertical", key)
        if should_skip_too_recent(cp, too_recent_seconds=too_recent_seconds):
            return {"fetched": 0, "inserted": 0, "skipped": 1}

        try:
            _, raw = _fetch_from_source(source, vertical_id)
        except Exception as e:
            log.warning("ingest_source_failed source=%s err=%s:%s", source, type(e).__name__, str(e))
            set_checkpoint("ingest_vertical", key, datetime.now(timezone.utc))
            return {"fetched": 0, "inserted": 0, "skipped": 0, "failed_sources": 1}

        enriched: list[dict[str, Any]] = []
        skipped_items = 0
        for it in raw:
            e = _enrich_signal(it, ctx=ctx, source=source)
            if e is None:
                skipped_items += 1
                continue
            enriched.append(e)

        fetched = len(enriched)
        out = _persist_with_writer(writer, enriched) if enriched else {"inserted": 0, "skipped": 0}
        set_checkpoint("ingest_vertical", key, datetime.now(timezone.utc))
        return {
            "fetched": fetched,
            "inserted": int(out.get("inserted") or 0),
            "skipped_db": int(out.get("skipped") or 0),
            "skipped_items": int(skipped_items),
        }
    finally:
        _CURRENT_CTX = None
