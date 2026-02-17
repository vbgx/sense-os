from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import HackerNewsClient
from .map import map_hit_to_signal


def fetch_signals(*, client: HackerNewsClient, ctx: FetchContext) -> Sequence[RawSignal]:
    # Optional cursor = page (0-based)
    page = 0
    if ctx.cursor:
        try:
            page = max(0, int(ctx.cursor))
        except Exception:
            page = 0

    hits = client.search_by_date(
        query=ctx.vertical_id,
        hits_per_page=ctx.limit,
        tags="story",
        page=page,
    )

    return [map_hit_to_signal(h, query=ctx.vertical_id) for h in hits]
