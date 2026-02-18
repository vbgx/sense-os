from __future__ import annotations

from typing import Sequence
from urllib.parse import quote_plus

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.adapters.rss import RssClient
from ingestion_worker.domain import RawSignal

from .map import map_rss_item_to_signal
from .types import GoogleNewsQuery


def build_google_news_rss_url(q: GoogleNewsQuery) -> str:
    # Search RSS endpoint:
    # https://news.google.com/rss/search?q=<q>&hl=<hl>&gl=<gl>&ceid=<gl>:<hl>
    return (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(q.q)}&hl={quote_plus(q.hl)}&gl={quote_plus(q.gl)}&ceid={quote_plus(q.ceid)}"
    )


def fetch_signals(*, client: RssClient, ctx: FetchContext) -> Sequence[RawSignal]:
    # Prefer ctx.query (actual search query). Fallback to vertical_id.
    query = (ctx.query or ctx.vertical_id or "").strip()
    if not query:
        return []

    q = GoogleNewsQuery(q=query)
    url = build_google_news_rss_url(q)

    try:
        items = client.fetch_feed(url=url, limit=ctx.limit) or []
    except Exception:
        items = []

    out: list[RawSignal] = []
    for it in items:
        try:
            out.append(map_rss_item_to_signal(item=it, query=query))
        except Exception:
            continue
    return out
