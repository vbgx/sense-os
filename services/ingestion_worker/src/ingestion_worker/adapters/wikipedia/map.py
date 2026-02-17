from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import WikipediaPageView, WikipediaRecentChange


def map_pageview_to_signal(pv: WikipediaPageView) -> RawSignal:
    """
    Pageviews = macro trend surface.
    Always classified as TREND.
    """

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.KNOWLEDGE_MACRO,
            name="wikipedia_pageviews",
            external_id=f"{pv.article}:{pv.timestamp_iso}",
            url=f"https://en.wikipedia.org/wiki/{pv.article}",
            extra={"metric": "pageviews"},
        ),
        title=f"Wikipedia trend: {pv.article}",
        body=f"{pv.views} daily views",
        created_at=pv.timestamp_iso,
        intent=SignalIntent.TREND,
        score_hint=float(pv.views),
        tags=(pv.article,),
        raw=pv.raw,
    )


def map_recent_change_to_signal(rc: WikipediaRecentChange) -> RawSignal:
    """
    Recent changes = evidence / activity surface.
    """

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.KNOWLEDGE_MACRO,
            name="wikipedia_recent_changes",
            external_id=str(rc.page_id),
            url=f"https://en.wikipedia.org/wiki/{rc.title.replace(' ', '_')}",
            extra={"metric": "recent_change"},
        ),
        title=f"Recent edit: {rc.title}",
        body=rc.comment or "",
        created_at=rc.timestamp_iso,
        author=rc.user,
        intent=SignalIntent.TREND,
        tags=(rc.title,),
        raw=rc.raw,
    )
