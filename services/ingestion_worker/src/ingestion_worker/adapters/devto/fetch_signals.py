from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import DevtoClient
from .map import map_article_to_signal


def fetch_signals(*, client: DevtoClient, ctx: FetchContext) -> Sequence[RawSignal]:
    articles = client.search(
        query=ctx.vertical_id,
        limit=ctx.limit,
    )

    return [
        map_article_to_signal(article=a, query=ctx.vertical_id)
        for a in articles
    ]
