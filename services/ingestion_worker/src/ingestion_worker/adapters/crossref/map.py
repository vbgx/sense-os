from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef

from .types import CrossrefWork


def map_work_to_signal(w: CrossrefWork, *, query: str) -> RawSignal:
    title = w.title or w.doi
    body_parts: list[str] = []

    if w.container_title:
        body_parts.append(f"Venue: {w.container_title}")
    if w.authors:
        body_parts.append("Authors: " + ", ".join(w.authors[:8]) + ("…" if len(w.authors) > 8 else ""))
    if w.abstract:
        body_parts.append(w.abstract)

    body = "\n".join(body_parts).strip()

    tags = []
    if w.subjects:
        tags.extend(list(w.subjects[:8]))
    tags.append(query)

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.RESEARCH,
            name="crossref",
            external_id=w.doi,
            url=w.url,
            extra={"query": query, "doi": w.doi},
        ),
        title=title,
        body=body,
        created_at=w.published_at_iso,
        author=None,
        tags=tuple(tags),
        intent=SignalIntent.EVIDENCE,
        score_hint=1.0,
        raw=w.raw,
    )
