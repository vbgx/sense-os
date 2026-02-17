from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from ingestion_worker.adapters.rss.types import RssItem


def map_rss_item_to_signal(*, item: RssItem, query: str) -> RawSignal:
    """
    Google News RSS = trend surface (not pain).
    """
    return RawSignal(
        source=SourceRef(
            kind=SourceKind.NEWS_RSS,
            name="googlenews",
            external_id=item.id or item.link,
            url=item.link,
            extra={"query": query},
        ),
        title=item.title or "",
        body=item.content or "",
        created_at=item.published_at,
        author=item.author,
        tags=(query,),
        intent=SignalIntent.TREND,
        score_hint=1.0,
        raw=item.raw,
    )
