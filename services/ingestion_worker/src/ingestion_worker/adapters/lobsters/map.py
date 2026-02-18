from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import LobstersStory


def map_story_to_signal(story: LobstersStory, *, query: str) -> RawSignal:
    meta = f"score={story.score} | comments={story.comment_count}"

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.BUILDERS_COMMUNITY,
            name="lobsters",
            external_id=story.short_id,
            url=story.url,
            extra={"query": query},
        ),
        title=story.title,
        body=meta,
        created_at=story.created_at_iso,
        author=None,
        tags=tuple(story.tags) + (query,),
        intent=SignalIntent.TREND,
        score_hint=float(story.score + story.comment_count),
        raw=story.raw,
    )
