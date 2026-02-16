from __future__ import annotations

from typing import List, Dict

from ingestion_worker.adapters.producthunt.fetch import fetch_producthunt_rss
from ingestion_worker.adapters.producthunt.map import map_producthunt_entry


def fetch_producthunt_signals(*, vertical_id: int, limit: int = 25) -> List[Dict]:
    entries = fetch_producthunt_rss(limit=limit)

    out: List[Dict] = []
    for entry in entries:
        mapped = map_producthunt_entry(entry, vertical_id=vertical_id)
        if mapped.get("content"):
            out.append(mapped)

    return out
