from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ingestion_worker.adapters._base import Adapter, FetchContext
from ingestion_worker.adapters.rss import RssClient
from ingestion_worker.domain import RawSignal, SourceKind

from .fetch_signals import fetch_signals


@dataclass
class GoogleNewsAdapter(Adapter):
    kind: SourceKind = SourceKind.NEWS_RSS
    name: str = "googlenews"

    client: RssClient | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            # IMPORTANT: give a real contact UA
            self.client = RssClient(user_agent="sense-os/0.1 (ingestion_worker; googlenews rss; contact: you@example.com)")

    def fetch(self, ctx: FetchContext) -> Sequence[RawSignal]:
        assert self.client is not None
        return fetch_signals(client=self.client, ctx=ctx)
