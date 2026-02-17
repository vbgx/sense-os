from __future__ import annotations

import re

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import MastodonStatus


def _strip_html(text: str) -> str:
    return re.sub("<[^<]+?>", "", text or "")


def map_status_to_signal(status: MastodonStatus, *, query: str) -> RawSignal:
    clean_body = _strip_html(status.content)
    score = status.reblogs_count + status.favourites_count

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.BUILDERS_COMMUNITY,
            name="mastodon",
            external_id=status.id,
            url=status.url,
            extra={"query": query},
        ),
        title=clean_body[:120],
        body=clean_body,
        created_at=status.created_at_iso,
        author=status.author,
        tags=(query,),
        intent=SignalIntent.TREND,
        score_hint=float(score),
        raw=status.raw,
    )
