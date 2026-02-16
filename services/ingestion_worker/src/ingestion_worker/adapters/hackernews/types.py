from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence


@dataclass(frozen=True)
class HNItem:
    id: int
    type: str
    by: Optional[str]
    time: int
    title: Optional[str]
    text: Optional[str]
    url: Optional[str]
    kids: Sequence[int]


def parse_hn_item(payload: dict[str, Any]) -> HNItem:
    return HNItem(
        id=int(payload["id"]),
        type=str(payload.get("type") or ""),
        by=payload.get("by"),
        time=int(payload.get("time") or 0),
        title=payload.get("title"),
        text=payload.get("text"),
        url=payload.get("url"),
        kids=tuple(int(x) for x in (payload.get("kids") or [])),
    )
