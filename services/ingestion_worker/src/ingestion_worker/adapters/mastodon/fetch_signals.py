from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import MastodonClient
from .map import map_status_to_signal


def fetch_signals(*, client: MastodonClient, ctx: FetchContext) -> Sequence[RawSignal]:
    statuses = client.search_statuses(
        query=ctx.vertical_id,
        limit=ctx.limit,
    )

    return [map_status_to_signal(s, query=ctx.vertical_id) for s in statuses]
