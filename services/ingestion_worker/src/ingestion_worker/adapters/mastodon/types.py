from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class MastodonStatus:
    id: str
    content: str
    url: Optional[str]
    created_at_iso: str
    author: Optional[str]
    reblogs_count: int
    favourites_count: int
    raw: Mapping[str, Any] | None = None
