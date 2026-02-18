from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class CrossrefWork:
    doi: str
    title: str
    abstract: Optional[str]
    published_at_iso: Optional[str]
    authors: Sequence[str]
    container_title: Optional[str]
    subjects: Sequence[str]
    url: Optional[str]
    raw: Mapping[str, Any] | None = None
