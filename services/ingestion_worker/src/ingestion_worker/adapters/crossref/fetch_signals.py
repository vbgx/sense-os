from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import CrossrefClient
from .map import map_work_to_signal


def fetch_signals(*, client: CrossrefClient, ctx: FetchContext) -> Sequence[RawSignal]:
    works = client.search_works(
        query=ctx.vertical_id,
        rows=ctx.limit,
        sort="relevance",
        order="desc",
        filters=None,
    )
    return [map_work_to_signal(w, query=ctx.vertical_id) for w in works]
