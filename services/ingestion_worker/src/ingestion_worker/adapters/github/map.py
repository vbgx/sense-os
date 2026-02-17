from __future__ import annotations

from ingestion_worker.domain import RawSignal, SignalIntent, SourceKind, SourceRef
from .types import GithubIssue


def map_issue_to_signal(issue: GithubIssue, *, query: str) -> RawSignal:
    body = issue.body[:1500] if issue.body else ""

    return RawSignal(
        source=SourceRef(
            kind=SourceKind.BUILDERS_COMMUNITY,
            name="github",
            external_id=f"{issue.repo_full_name}#{issue.number}",
            url=issue.html_url,
            extra={"query": query},
        ),
        title=issue.title,
        body=body,
        created_at=issue.created_at,
        author=issue.author,
        tags=tuple(issue.labels) + (query,),
        intent=SignalIntent.EVIDENCE,
        score_hint=1.0,
        raw=issue.raw,
    )
