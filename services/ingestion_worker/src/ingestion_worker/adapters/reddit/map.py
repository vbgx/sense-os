from __future__ import annotations

from typing import Any, Dict

from ingestion_worker.adapters.reddit.types import RssItem
from ingestion_worker.normalize.dates import to_utc_datetime


def map_post_to_signal(post: RssItem, *, vertical_id: int, source: str) -> Dict[str, Any]:
    return {
        "vertical_id": int(vertical_id),
        "source": str(source),
        "external_id": str(post.external_id),
        "content": str(post.content or post.title),
        "url": post.url,
        "created_at": to_utc_datetime(getattr(post, "created_at_iso", None)),
    }
