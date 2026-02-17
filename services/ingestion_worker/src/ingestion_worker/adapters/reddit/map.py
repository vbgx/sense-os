from __future__ import annotations

from typing import Any, Dict

from ingestion_worker.adapters.reddit.types import RssItem
from ingestion_worker.normalize.dates import to_utc_datetime


def map_post_to_signal(
    post: RssItem,
    *,
    vertical_id: str,
    vertical_db_id: int | None,
    taxonomy_version: str | None,
    source: str,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "vertical_id": str(vertical_id),
        "source": str(source),
        "external_id": str(post.external_id),
        "content": str(post.content or post.title),
        "url": post.url,
        "created_at": to_utc_datetime(getattr(post, "created_at_iso", None)),
    }
    if vertical_db_id is not None:
        data["vertical_db_id"] = int(vertical_db_id)
    if taxonomy_version is not None:
        data["taxonomy_version"] = str(taxonomy_version)
    return data
