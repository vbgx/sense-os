from dataclasses import dataclass
from typing import Sequence

from ingestion_worker.adapters._base import Adapter, FetchContext
from domain.verticals.contract_v1 import RawSignal
from ingestion_worker.domain.sources import SourceKind

from .client import StackExchangeClient
from .fetch_signals import fetch_signals


@dataclass
class StackExchangeAdapter(Adapter):
    kind: SourceKind = SourceKind.BUILDERS_QA
    name: str = "stackexchange"

    client: StackExchangeClient | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = StackExchangeClient()

    def fetch(self, ctx: FetchContext) -> Sequence[RawSignal]:
        return fetch_signals(client=self.client, ctx=ctx)
