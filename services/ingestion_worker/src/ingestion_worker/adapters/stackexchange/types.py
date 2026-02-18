from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class StackExchangeQuestion:
    question_id: int
    site: str
    title: str | None = None
    link: str | None = None
    tags: Sequence[str] | None = None
    score: int | None = None
    answer_count: int | None = None
    body: str | None = None
    creation_date_iso: Optional[str] = None
    owner_display_name: Optional[str] = None
    raw: Mapping[str, Any] | None = None
