from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import LOBSTERS_LIMITER
from .types import LobstersStory


@dataclass
class LobstersClient:
    base_url: str = "https://lobste.rs"
    timeout_s: float = 15.0

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": settings.sense_ua,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )

    def _map(self, item: dict) -> LobstersStory:
        tags = []
        for t in (item.get("tags") or []) or []:
            if isinstance(t, dict) and t.get("tag"):
                tags.append(str(t["tag"]))

        short_id = item.get("short_id") or ""
        url = item.get("url") or (f"{self.base_url}/s/{short_id}" if short_id else self.base_url)

        return LobstersStory(
            short_id=short_id,
            title=item.get("title") or "",
            url=url,
            score=int(item.get("score") or 0),
            comment_count=int(item.get("comment_count") or 0),
            created_at_iso=item.get("created_at"),
            tags=tuple(tags),
            raw=item,
        )

    def fetch_newest(self, *, limit: int = 20) -> Sequence[LobstersStory]:
        LOBSTERS_LIMITER.acquire()
        url = f"{self.base_url}/newest.json"

        with self._client() as c:
            r = c.get(url)
            r.raise_for_status()
            data = r.json()

        return [self._map(item) for item in (data or [])[:limit]]

    def fetch_by_tag(self, *, tag: str, limit: int = 20) -> Sequence[LobstersStory]:
        """
        Returns [] if tag does not exist (404).
        """
        LOBSTERS_LIMITER.acquire()
        url = f"{self.base_url}/t/{tag}.json"

        with self._client() as c:
            r = c.get(url)
            if r.status_code == 404:
                return []
            r.raise_for_status()
            data = r.json()

        return [self._map(item) for item in (data or [])[:limit]]
