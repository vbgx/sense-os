from __future__ import annotations

from typing import List, Dict

from ingestion_worker.adapters.producthunt.fetch import fetch_producthunt_rss
from ingestion_worker.adapters.producthunt.map import map_producthunt_entry


def fetch_producthunt_signals(
    *,
    vertical_id: str,
    vertical_db_id: int | None,
    taxonomy_version: str | None,
    limit: int = 25,
) -> List[Dict]:
    entries = fetch_producthunt_rss(limit=limit)

    out: List[Dict] = []
    for entry in entries:
        mapped = map_producthunt_entry(
            entry,
            vertical_id=vertical_id,
            vertical_db_id=vertical_db_id,
            taxonomy_version=taxonomy_version,
        )
        if mapped.get("content"):
            out.append(mapped)

    return out

def fetch_producthunt_signals(*, vertical_id: str, taxonomy_version: str, vertical_db_id: int):
    return fetch_signals(vertical_id=vertical_id, taxonomy_version=taxonomy_version, vertical_db_id=vertical_db_id)
