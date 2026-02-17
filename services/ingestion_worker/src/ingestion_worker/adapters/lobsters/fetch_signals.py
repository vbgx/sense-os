from __future__ import annotations

from typing import Sequence

from ingestion_worker.adapters._base import FetchContext
from ingestion_worker.domain import RawSignal

from .client import LobstersClient
from .map import map_story_to_signal


def fetch_signals(*, client: LobstersClient, ctx: FetchContext) -> Sequence[RawSignal]:
    # Heuristic:
    # - try tag if single token
    # - fallback to newest if tag doesn't exist
    stories = []
    if " " not in ctx.vertical_id:
        stories = list(client.fetch_by_tag(tag=ctx.vertical_id, limit=ctx.limit))

    if not stories:
        stories = list(client.fetch_newest(limit=ctx.limit))

    return [map_story_to_signal(s, query=ctx.vertical_id) for s in stories]
