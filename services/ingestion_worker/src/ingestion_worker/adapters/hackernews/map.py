from __future__ import annotations

from typing import Any, Dict

from ingestion_worker.adapters.hackernews.types import HNItem
from ingestion_worker.normalize.clean_text import clean_text
from ingestion_worker.normalize.dates import to_utc_datetime


def map_hn_story_to_signal_dict(item: HNItem, raw: dict, *, vertical_id: int, kind: str) -> Dict[str, Any]:
    url = item.url or f"https://news.ycombinator.com/item?id={item.id}"
    title = item.title or ""
    text = item.text or ""
    content = clean_text(f"{title}\n\n{text}".strip()) or clean_text(title) or clean_text(text)

    return {
        "vertical_id": int(vertical_id),
        "source": "hackernews",
        "external_id": f"hn:{int(item.id)}",
        "content": content,
        "url": url,
        "created_at": to_utc_datetime(item.time),
    }


def map_hn_comment_to_signal_dict(item: HNItem, raw: dict, *, vertical_id: int, parent_story_id: int) -> Dict[str, Any]:
    url = f"https://news.ycombinator.com/item?id={int(item.id)}"
    text = item.text or ""
    content = clean_text(text)

    return {
        "vertical_id": int(vertical_id),
        "source": "hackernews",
        "external_id": f"hn:{int(item.id)}",
        "content": content,
        "url": url,
        "created_at": to_utc_datetime(item.time),
    }
