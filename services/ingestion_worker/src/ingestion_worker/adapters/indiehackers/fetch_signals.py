from __future__ import annotations

from typing import List, Dict

from ingestion_worker.adapters.indiehackers.fetch import fetch_indiehackers_rss
from ingestion_worker.adapters.indiehackers.map import map_indiehackers_entry


def fetch_indiehackers_signals(*, vertical_id: int, limit: int = 25) -> List[Dict]:
    entries = fetch_indiehackers_rss(limit=limit)

    out: List[Dict] = []
    for entry in entries:
        mapped = map_indiehackers_entry(entry, vertical_id=vertical_id)
        if mapped.get("content"):
            out.append(mapped)

    return out
