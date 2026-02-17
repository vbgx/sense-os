from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef

from .types import DevtoArticle


def map_article_to_signal(article: DevtoArticle, *, query: str) -> RawSignal:
    return RawSignal(
        source=SourceRef(
            kind=SourceKind.BUILDER_COMMUNITY,
            name="devto",
            external_id=str(article.id),
            url=article.url,
            extra={"query": query},
        ),
        title=article.title,
        body=article.description,
        created_at=article.published_at_iso,
        author=article.author,
        tags=tuple(article.tags) + (query,),
        intent=SignalIntent.TREND,
        score_hint=1.0,
        raw=article.raw,
    )
