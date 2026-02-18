from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import WikipediaClient
from .map import map_pageview_to_signal, map_recent_change_to_signal


def fetch_signals(*, client: WikipediaClient, ctx: FetchContext) -> Sequence[RawSignal]:
    signals: list[RawSignal] = []

    q = (ctx.query or ctx.vertical_id or "").strip()
    if not q:
        return []

    try:
        pageviews = client.fetch_pageviews(article=q, limit=ctx.limit) or []
    except Exception:
        pageviews = []
    for pv in pageviews:
        try:
            signals.append(map_pageview_to_signal(pv))
        except Exception:
            continue

    try:
        changes = client.fetch_recent_changes(query=q, limit=ctx.limit) or []
    except Exception:
        changes = []
    for rc in changes:
        try:
            signals.append(map_recent_change_to_signal(rc))
        except Exception:
            continue

    return signals
