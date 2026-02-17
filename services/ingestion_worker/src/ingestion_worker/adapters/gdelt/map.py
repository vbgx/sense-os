from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef

from .types import GdeltArticle


def map_article_to_signal(article: GdeltArticle, *, query: str) -> RawSignal:
    return RawSignal(
        source=SourceRef(
            kind=SourceKind.NEWS_RSS,
            name="gdelt",
            external_id=article.url,
            url=article.url,
            extra={"query": query},
        ),
        title=article.title,
        body=f"Domain: {article.domain or ''}\nCountry: {article.source_country or ''}",
        created_at=article.published_at_iso,
        author=None,
        tags=(query,),
        intent=SignalIntent.TREND,
        score_hint=1.0,
        raw=article.raw,
    )
