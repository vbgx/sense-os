from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class HNItem:
    id: int
    title: str | None
    text: str | None
    url: str | None
    by: str | None
    time: int | None
    score: int | None


def parse_hn_item(payload: dict[str, Any]) -> HNItem:
    return HNItem(
        id=int(payload.get("id") or 0),
        title=payload.get("title"),
        text=payload.get("text"),
        url=payload.get("url"),
        by=payload.get("by"),
        time=payload.get("time"),
        score=payload.get("score"),
    )


def hn_created_at(item: HNItem) -> datetime:
    ts = int(item.time or 0)
    return datetime.fromtimestamp(ts, tz=timezone.utc)
