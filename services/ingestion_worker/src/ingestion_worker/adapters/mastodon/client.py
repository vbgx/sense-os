from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import MASTODON_LIMITER
from .types import MastodonStatus


@dataclass
class MastodonClient:
    timeout_s: float = 20.0

    def _base_url(self) -> str:
        return os.getenv("MASTODON_BASE_URL", "https://mastodon.social").rstrip("/")

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": settings.sense_ua,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )

    def search_statuses(self, *, query: str, limit: int = 20) -> Sequence[MastodonStatus]:
        MASTODON_LIMITER.acquire()

        url = f"{self._base_url()}/api/v2/search"
        params = {
            "q": query,
            "type": "statuses",
            "limit": min(max(limit, 1), 40),
        }

        with self._client() as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        statuses = (data.get("statuses") or []) if isinstance(data, dict) else []

        out: list[MastodonStatus] = []

        for s in statuses:
            account = s.get("account") or {}

            out.append(
                MastodonStatus(
                    id=s.get("id"),
                    content=s.get("content") or "",
                    url=s.get("url"),
                    created_at_iso=s.get("created_at"),
                    author=account.get("acct"),
                    reblogs_count=int(s.get("reblogs_count") or 0),
                    favourites_count=int(s.get("favourites_count") or 0),
                    raw=s,
                )
            )

        return out
