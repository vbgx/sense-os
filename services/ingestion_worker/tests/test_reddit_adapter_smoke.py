from __future__ import annotations

import json
from pathlib import Path

from ingestion_worker.adapters.reddit.map import map_post_to_signal
from ingestion_worker.adapters.reddit.types import RssItem


def test_reddit_adapter_smoke_maps_fixture():
    root = Path(__file__).resolve().parents[3]
    sample_path = root / "tools" / "fixtures" / "samples" / "reddit_post.json"
    raw = json.loads(sample_path.read_text())

    item = RssItem(
        external_id=str(raw["id"]),
        title=str(raw["title"]),
        content=str(raw.get("selftext") or raw.get("title") or ""),
        url=None,
        created_at_iso=None,
    )
    signal = map_post_to_signal(item, vertical_id=1, source="reddit")

    assert signal["vertical_id"] == 1
    assert signal["source"] == "reddit"
    assert signal["external_id"] == raw["id"]
    assert "content" in signal
