from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import ArxivClient
from .map import map_entry_to_signal


def fetch_signals(*, client: ArxivClient, ctx: FetchContext) -> Sequence[RawSignal]:
    papers = client.search(
        query=ctx.vertical_id,
        max_results=ctx.limit,
        sort_by="submittedDate",
        sort_order="descending",
    )
    return [map_entry_to_signal(p, query=ctx.vertical_id) for p in papers]
