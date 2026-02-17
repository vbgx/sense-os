from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import WikipediaClient
from .map import map_pageview_to_signal, map_recent_change_to_signal


def fetch_signals(*, client: WikipediaClient, ctx: FetchContext) -> Sequence[RawSignal]:
    signals: list[RawSignal] = []

    pageviews = client.fetch_pageviews(article=ctx.vertical_id, limit=ctx.limit)
    for pv in pageviews:
        signals.append(map_pageview_to_signal(pv))

    changes = client.fetch_recent_changes(query=ctx.vertical_id, limit=ctx.limit)
    for rc in changes:
        signals.append(map_recent_change_to_signal(rc))

    return signals
