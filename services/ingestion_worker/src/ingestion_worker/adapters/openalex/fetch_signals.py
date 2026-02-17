from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import OpenAlexClient
from .map import map_work_to_signal


def fetch_signals(*, client: OpenAlexClient, ctx: FetchContext) -> Sequence[RawSignal]:
    works = client.search_works(
        query=ctx.vertical_id,
        per_page=ctx.limit,
    )
    return [map_work_to_signal(w, query=ctx.vertical_id) for w in works]
