from __future__ import annotations

from typing import Any

from ingestion_worker.adapters.hackernews.types import HNItem, hn_created_at


def _content_from_item(item: HNItem, raw: dict[str, Any] | None = None) -> str:
    parts: list[str] = []
    if item.title:
        parts.append(str(item.title))
    if item.text:
        parts.append(str(item.text))
    if not parts and raw:
        t = raw.get("text") or raw.get("title")
        if isinstance(t, str):
            parts.append(t)
    return "\n".join(p for p in parts if p).strip()


def _base_signal(
    item: HNItem,
    raw: dict[str, Any] | None,
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
) -> dict[str, Any]:
    return {
        "vertical_id": str(vertical_id),
        "vertical_db_id": int(vertical_db_id),
        "taxonomy_version": str(taxonomy_version),
        "source": "hackernews",
        "external_id": f"hn:{int(item.id)}",
        "content": _content_from_item(item, raw),
        "url": item.url,
    }


def map_hn_item_to_signal_dict(
    item: HNItem,
    raw: dict[str, Any] | None = None,
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
) -> dict[str, Any]:
    return _base_signal(
        item,
        raw,
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
    )


def map_hn_story_to_signal_dict(
    item: HNItem,
    raw: dict[str, Any] | None = None,
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    kind: str | None = None,
) -> dict[str, Any]:
    _ = kind
    return _base_signal(
        item,
        raw,
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
    )


def map_hn_comment_to_signal_dict(
    item: HNItem,
    raw: dict[str, Any] | None = None,
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    parent_story_id: int | None = None,
) -> dict[str, Any]:
    _ = parent_story_id
    return _base_signal(
        item,
        raw,
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
    )
