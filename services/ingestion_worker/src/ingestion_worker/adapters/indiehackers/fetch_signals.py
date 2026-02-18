from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import IndieHackersClient
from .map import map_indiehackers_entry


def _to_entry(item) -> dict:
    return {
        "guid": item.id or item.link,
        "title": item.title or "",
        "summary": item.content or "",
        "link": item.link or "",
        "published": item.published_at,
    }


def fetch_signals(*, client: IndieHackersClient, ctx: FetchContext) -> Sequence[RawSignal]:
    items = list(client.fetch_recent(limit=ctx.limit))
    query = (ctx.query or "").strip().lower()

    def _matches(item) -> bool:
        if not query:
            return True
        entry = _to_entry(item)
        hay = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        return query in hay

    filtered = [i for i in items if _matches(i)] if query else items
    if query and not filtered:
        filtered = items

    out: list[RawSignal] = []
    for item in filtered:
        entry = _to_entry(item)
        mapped = map_indiehackers_entry(
            entry,
            vertical_id=ctx.vertical_id,
            vertical_db_id=ctx.vertical_db_id,
            taxonomy_version=ctx.taxonomy_version,
        )
        mapped.pop("language", None)
        if mapped.get("content"):
            out.append(mapped)

    return out
