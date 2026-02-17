from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from ingestion_worker.normalize.clean_text import clean_text
from ingestion_worker.normalize.normalize_signal import NormalizedSignal


def _unix_to_dt(ts: int) -> Optional[datetime]:
    if not ts:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc)


def normalize_hn_story(*, item_id: int, title: str, text: str, url: Optional[str], created_at_unix: int) -> NormalizedSignal:
    content = clean_text(f"{title}\n\n{text}".strip())
    return NormalizedSignal(
        source="hackernews",
        external_id=f"hn:{int(item_id)}",
        content=content,
        url=url,
        created_at=_unix_to_dt(created_at_unix),
    )


def normalize_hn_comment(*, item_id: int, parent_story_id: int, text: str, created_at_unix: int) -> NormalizedSignal:
    content = clean_text(text)
    return NormalizedSignal(
        source="hackernews",
        external_id=f"hn:{int(item_id)}",
        content=content,
        url=f"https://news.ycombinator.com/item?id={int(item_id)}",
        created_at=_unix_to_dt(created_at_unix),
    )
