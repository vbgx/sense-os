from __future__ import annotations

import logging
from typing import Any

from ingestion_worker.adapters import registry
from ingestion_worker.pipeline.fanout import dedup_signals, fanout_fetch
from ingestion_worker.settings import SOURCES_DEFAULT
from ingestion_worker.storage.signals_writer import SignalsWriter

log = logging.getLogger(__name__)


def ingest_vertical(job: dict[str, Any]) -> dict[str, int]:
    vertical_id = str(job["vertical_id"])
    taxonomy_version = str(job["taxonomy_version"])
    vertical_db_id = job.get("vertical_db_id")
    vertical_db_id = int(vertical_db_id) if vertical_db_id is not None else None
    if vertical_db_id is None:
        raise ValueError("job missing vertical_db_id")

    # New: fanout sources (job overrides defaults)
    sources = job.get("sources")
    if isinstance(sources, list) and all(isinstance(x, str) for x in sources):
        sources_list = [str(x) for x in sources]
    else:
        sources_list = [str(x) for x in SOURCES_DEFAULT]

    writer = SignalsWriter()

    def _fetch_one(source: str) -> list[dict[str, Any]]:
        # Pattern A: adapter instance
        get_adapter = getattr(registry, "get_adapter", None)
        if callable(get_adapter):
            adapter = get_adapter(source)
            fn = getattr(adapter, "fetch_signals", None)
            if not callable(fn):
                raise RuntimeError(f"adapter {source} has no fetch_signals()")
            return fn(vertical_id=vertical_id, taxonomy_version=taxonomy_version, vertical_db_id=vertical_db_id)

        # Pattern B: module-level fetch function
        fetch = getattr(registry, "fetch_signals", None)
        if callable(fetch):
            return fetch(source=source, vertical_id=vertical_id, taxonomy_version=taxonomy_version, vertical_db_id=vertical_db_id)

        raise RuntimeError("adapters.registry must expose get_adapter() or fetch_signals()")

    # Fanout
    res = fanout_fetch(sources=sources_list, fetch_fn=_fetch_one)

    # Flatten + dedup
    flat: list[tuple[str, dict[str, Any]]] = []
    for r in res:
        for it in r.items:
            # stamp source if not present
            if "source" not in it:
                it = dict(it)
                it["source"] = r.source
            flat.append((r.source, it))

    deduped = dedup_signals(flat)

    # Persist once
    writer.write_signals(
        deduped,
        vertical_db_id=int(vertical_db_id),
        taxonomy_version=str(taxonomy_version),
    )

    # Metrics
    per_source_total = sum(len(r.items) for r in res)
    per_source_ok = sum(1 for r in res if not r.error)
    per_source_err = sum(1 for r in res if r.error)

    log.info(
        "ingest_vertical fanout done vertical_db_id=%s sources=%s ok=%s err=%s total=%s deduped=%s",
        vertical_db_id,
        ",".join(sources_list),
        per_source_ok,
        per_source_err,
        per_source_total,
        len(deduped),
    )

    return {
        "sources": int(len(sources_list)),
        "sources_ok": int(per_source_ok),
        "sources_err": int(per_source_err),
        "signals_raw": int(per_source_total),
        "signals_deduped": int(len(deduped)),
    }
