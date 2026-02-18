from __future__ import annotations

from typing import Any, Iterable

from ingestion_worker.adapters._base import BaseAdapter, FetchContext
from ingestion_worker.adapters.hackernews.fetch_signals import fetch_hackernews_signals


class HackerNewsAdapter(BaseAdapter):
    source = "hackernews"

    def fetch_signals(self, ctx: FetchContext, **kwargs: Any) -> Iterable[dict[str, Any]]:
        return fetch_hackernews_signals(
            vertical_id=ctx.vertical_id,
            query=ctx.query,
            limit=ctx.limit,
            vertical_db_id=ctx.vertical_db_id,
            taxonomy_version=ctx.taxonomy_version,
            **kwargs,
        )
