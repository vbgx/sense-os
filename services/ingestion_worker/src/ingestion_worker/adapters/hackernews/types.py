from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class HackerNewsHit:
    object_id: str
    title: str
    url: Optional[str]
    author: Optional[str]
    points: int
    num_comments: int
    created_at_iso: str
    story_text: Optional[str]
    tags: tuple[str, ...]
    raw: Mapping[str, Any] | None = None
