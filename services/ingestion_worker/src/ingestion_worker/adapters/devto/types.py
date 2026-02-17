from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class DevtoArticle:
    id: int
    title: str
    description: str
    url: str
    published_at_iso: str
    tags: Sequence[str]
    author: str | None
    raw: Mapping[str, Any] | None = None
