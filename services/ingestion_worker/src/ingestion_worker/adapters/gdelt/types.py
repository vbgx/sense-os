from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class GdeltArticle:
    url: str
    title: str
    source_country: Optional[str]
    language: Optional[str]
    published_at_iso: Optional[str]
    domain: Optional[str]
    raw: Mapping[str, Any] | None = None
