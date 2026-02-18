from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class ArxivPaper:
    id: str
    title: str
    summary: str
    published: str
    updated: str
    authors: Sequence[str]
    primary_category: Optional[str]
    raw: dict | None = None
