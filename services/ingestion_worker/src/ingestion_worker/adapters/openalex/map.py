from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import OpenAlexWork


def map_work_to_signal(w: OpenAlexWork, *, query: str) -> RawSignal:
    body_parts: list[str] = []

    if w.host_venue:
        body_parts.append(f"Venue: {w.host_venue}")
    if w.authors:
        body_parts.append("Authors: " + ", ".join(list(w.authors)[:8]) + ("…" if len(w.authors) > 8 else ""))
    if w.abstract:
        body_parts.append(w.abstract)

    body = "\n".join([p for p in body_parts if p]).strip()

    tags = []
    tags.extend(list(w.concepts[:10]))
    tags.append(query)

    score = float(w.cited_by_count or 0)

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.RESEARCH,
            name="openalex",
            external_id=w.id,
            url=w.url or w.id,
            extra={"query": query, "doi": w.doi, "cited_by_count": w.cited_by_count},
        ),
        title=w.title or w.id,
        body=body,
        created_at=w.published_at,
        author=None,
        tags=tuple(tags),
        intent=SignalIntent.EVIDENCE,
        score_hint=score,
        raw=w.raw,
    )
