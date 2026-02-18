from __future__ import annotations

from typing import Any

from ingestion_worker.adapters.hackernews.types import HNItem, hn_created_at


def _base(item: HNItem, *, vertical_db_id: int, taxonomy_version: str) -> dict[str, Any]:
    created_at = hn_created_at(item).isoformat().replace("+00:00", "Z")
    return {
        "vertical_db_id": int(vertical_db_id),
        "taxonomy_version": str(taxonomy_version),
        "source": "hackernews",
        "source_external_id": f"hn:{int(item.id)}",
        "title": item.title or "",
        "text": item.text or "",
        "url": item.url,
        "created_at": created_at,
        "author": item.by,
        "score": int(item.score or 0),
    }


def map_hn_item_to_signal_dict(item: HNItem, *, vertical_db_id: int, taxonomy_version: str) -> dict[str, Any]:
    return _base(item, vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)


def map_hn_story_to_signal_dict(item: HNItem, *, vertical_db_id: int, taxonomy_version: str) -> dict[str, Any]:
    return _base(item, vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)


def map_hn_comment_to_signal_dict(item: HNItem, *, vertical_db_id: int, taxonomy_version: str) -> dict[str, Any]:
    return _base(item, vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)
