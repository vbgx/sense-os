from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ingestion_worker.adapters._base import Adapter, FetchContext
from ingestion_worker.domain import RawSignal, SourceKind

from .client import ProductHuntClient
from .fetch_signals import fetch_signals


@dataclass
class ProductHuntAdapter(Adapter):
    kind: SourceKind = SourceKind.BUILDERS_COMMUNITY
    name: str = "producthunt"

    client: ProductHuntClient | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = ProductHuntClient()

    def fetch(self, ctx: FetchContext) -> Sequence[RawSignal]:
        assert self.client is not None
        return fetch_signals(client=self.client, ctx=ctx)
