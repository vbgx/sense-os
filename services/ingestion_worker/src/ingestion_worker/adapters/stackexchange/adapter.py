from dataclasses import dataclass
from typing import Sequence

from adapters._base import Adapter, FetchContext
from domain import RawSignal, SourceKind

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
