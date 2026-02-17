from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import GithubClient
from .map import map_issue_to_signal


def fetch_signals(*, client: GithubClient, ctx: FetchContext) -> Sequence[RawSignal]:
    issues = client.search_issues(
        query=ctx.vertical_id,
        per_page=ctx.limit,
    )

    return [map_issue_to_signal(i, query=ctx.vertical_id) for i in issues]
