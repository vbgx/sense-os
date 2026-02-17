from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import HackerNewsHit


def map_hit_to_signal(hit: HackerNewsHit, *, query: str) -> RawSignal:
    # Body: keep it short; we mostly want the title + metadata
    meta = []
    meta.append(f"points={hit.points}")
    meta.append(f"comments={hit.num_comments}")
    if hit.author:
        meta.append(f"author={hit.author}")
    meta_s = " | ".join(meta)

    body = (hit.story_text or "").strip()
    if body and len(body) > 1200:
        body = body[:1200] + "…"

    tags = list(hit.tags[:10])
    tags.append(query)

    url = hit.url or f"https://news.ycombinator.com/item?id={hit.object_id}"

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.BUILDERS_COMMUNITY,
            name="hackernews",
            external_id=hit.object_id,
            url=url,
            extra={"query": query, "points": hit.points, "comments": hit.num_comments},
        ),
        title=hit.title or f"HN item {hit.object_id}",
        body=(meta_s + ("\n" + body if body else "")).strip(),
        created_at=hit.created_at_iso or None,
        author=hit.author,
        tags=tuple(tags),
        intent=SignalIntent.TREND,
        score_hint=float(hit.points + hit.num_comments),
        raw=hit.raw,
    )
