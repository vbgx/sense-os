from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Optional


@dataclass(frozen=True)
class GithubIssue:
    id: int
    number: int
    title: str
    body: str
    html_url: str
    repo_full_name: str
    state: str
    created_at: str
    updated_at: str
    author: Optional[str]
    labels: Sequence[str]
    raw: Mapping[str, Any] | None = None
