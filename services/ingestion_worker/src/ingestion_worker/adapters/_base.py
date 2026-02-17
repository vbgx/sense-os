from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from ingestion_worker.domain import RawSignal, SourceKind


@dataclass(frozen=True)
class FetchContext:
    vertical_id: str
    limit: int = 100
    cursor: str | None = None


class Adapter(Protocol):
    kind: SourceKind
    name: str

    def fetch(self, ctx: FetchContext) -> Sequence[RawSignal]:
        ...
