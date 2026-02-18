from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ingestion_worker.adapters._base import Adapter, FetchContext
from ingestion_worker.domain import RawSignal, SourceKind

from .client import WikipediaClient
from .fetch_signals import fetch_signals


@dataclass
class WikipediaAdapter(Adapter):
    kind: SourceKind = SourceKind.KNOWLEDGE_MACRO
    name: str = "wikipedia"

    client: WikipediaClient | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = WikipediaClient()

    def fetch(self, ctx: FetchContext) -> Sequence[RawSignal]:
        if self.client is None:
            return []
        try:
            out = fetch_signals(client=self.client, ctx=ctx)
            return out or []
        except Exception:
            return []
