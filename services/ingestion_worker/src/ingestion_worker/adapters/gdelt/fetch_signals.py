from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import GdeltClient
from .map import map_article_to_signal


def fetch_signals(*, client: GdeltClient, ctx: FetchContext) -> Sequence[RawSignal]:
    articles = client.search(
        query=ctx.vertical_id,
        max_records=ctx.limit,
        timespan="7d",
    )

    return [
        map_article_to_signal(article=a, query=ctx.vertical_id)
        for a in articles
    ]
