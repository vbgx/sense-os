from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef

from .types import ArxivPaper


def map_paper_to_trend_signal(p: ArxivPaper) -> dict:
    """
    Legacy/minimal dict representation (kept for compatibility / debugging).
    """
    return {
        "source": "arxiv",
        "id": p.id,
        "title": p.title,
        "body": p.summary,
        "published": p.published,
        "authors": p.authors,
        "category": p.primary_category,
        "intent": "evidence",
        "score_hint": 1.0,
    }


def map_entry_to_signal(p: ArxivPaper, *, query: str) -> RawSignal:
    """
    Canonical mapper used by ingestion_worker adapters.
    """
    tags = []
    if getattr(p, "primary_category", None):
        tags.append(str(p.primary_category))
    tags.append(query)

    # Best-effort URL: arXiv ids can be like "http://arxiv.org/abs/xxxx" or "xxxx"
    pid = str(getattr(p, "id", "") or "")
    url = None
    if pid.startswith("http://") or pid.startswith("https://"):
        url = pid
        external_id = pid.rsplit("/", 1)[-1]
    else:
        external_id = pid
        url = f"https://arxiv.org/abs/{external_id}" if external_id else None

    title = (getattr(p, "title", "") or "").strip() or external_id or "arXiv paper"
    body = (getattr(p, "summary", "") or "").strip()

    # authors can be list[str] or str
    authors = getattr(p, "authors", None)
    author_s = None
    if isinstance(authors, list):
        author_s = ", ".join([str(a) for a in authors[:8]]) + ("…" if len(authors) > 8 else "")
    elif isinstance(authors, str):
        author_s = authors.strip() or None

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.RESEARCH,
            name="arxiv",
            external_id=external_id or pid,
            url=url,
            extra={"query": query, "category": getattr(p, "primary_category", None)},
        ),
        title=title,
        body=body,
        created_at=getattr(p, "published", None),
        author=author_s,
        tags=tuple(tags),
        intent=SignalIntent.EVIDENCE,
        score_hint=1.0,
        raw={"paper": map_paper_to_trend_signal(p)},
    )
