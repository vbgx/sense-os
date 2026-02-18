from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class WikipediaPageView:
    article: str
    views: int
    timestamp_iso: str
    raw: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class WikipediaRecentChange:
    page_id: int
    title: str
    user: Optional[str]
    comment: Optional[str]
    timestamp_iso: str
    raw: Mapping[str, Any] | None = None
