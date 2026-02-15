from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RssItem:
    external_id: str
    title: str
    content: str
    url: str | None
    created_at_iso: str | None
