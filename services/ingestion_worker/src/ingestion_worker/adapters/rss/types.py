from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class RssItem:
    id: str
    title: str
    link: str
    content: str
    published_at: Optional[str] = None
    author: Optional[str] = None
    raw: Mapping[str, Any] | None = None
