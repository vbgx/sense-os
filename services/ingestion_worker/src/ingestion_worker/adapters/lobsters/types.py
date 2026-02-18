from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class LobstersStory:
    short_id: str
    title: str
    url: str
    score: int
    comment_count: int
    created_at_iso: str
    tags: Sequence[str]
    raw: Mapping[str, Any] | None = None
