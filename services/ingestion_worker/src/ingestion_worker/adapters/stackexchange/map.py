from domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import StackExchangeQuestion


def map_question_to_signal(q: StackExchangeQuestion) -> RawSignal:
    return RawSignal(
        source=SourceRef(
            kind=SourceKind.BUILDERS_QA,
            name="stackexchange",
            external_id=str(q.question_id),
            url=q.link,
            extra={"site": q.site, "score": q.score},
        ),
        title=q.title or "",
        body=q.body or "",
        created_at=q.creation_date_iso,
        author=q.owner_display_name,
        tags=tuple(q.tags or []),
        intent=SignalIntent.PAIN,
        score_hint=float(q.score or 0),
        raw=q.raw,
    )
