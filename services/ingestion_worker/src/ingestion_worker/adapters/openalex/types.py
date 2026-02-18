from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class OpenAlexWork:
    id: str
    doi: Optional[str]
    title: str
    abstract: Optional[str]
    published_at: Optional[str]
    updated_at: Optional[str]
    authors: Sequence[str]
    host_venue: Optional[str]
    cited_by_count: int
    concepts: Sequence[str]
    url: Optional[str]
    raw: Mapping[str, Any] | None = None
