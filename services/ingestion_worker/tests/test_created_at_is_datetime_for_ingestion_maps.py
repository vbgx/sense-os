from __future__ import annotations

from datetime import datetime
from ingestion_worker.adapters.producthunt.map import map_producthunt_entry
from ingestion_worker.adapters.indiehackers.map import map_indiehackers_entry


def test_rss_maps_emit_datetime_created_at():
    ih = map_indiehackers_entry(
        {
            "guid": "g1",
            "title": "Title",
            "summary": "Body",
            "link": "https://x",
            "published": "2026-02-16T12:00:00+00:00",
        },
        vertical_id=1,
    )
    assert isinstance(ih["created_at"], datetime)

    ph = map_producthunt_entry(
        {
            "guid": "g2",
            "title": "Title",
            "summary": "<p>Body</p>",
            "link": "https://y",
            "published": "2026-02-16T12:00:00+00:00",
        },
        vertical_id=1,
    )
    assert isinstance(ph["created_at"], datetime)
