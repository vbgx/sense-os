from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import os
import httpx

from .parse import parse_feed
from .types import RssItem


DEFAULT_UA = os.environ.get(
    "SENSE_UA",
    "sense-os/0.1 (ingestion_worker; contact: you@example.com)",
)


@dataclass
class RssClient:
    timeout_s: float = 20.0
    user_agent: str = DEFAULT_UA

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
            },
            follow_redirects=True,
        )

    def fetch_feed(self, *, url: str, limit: int = 100) -> Sequence[RssItem]:
        with self._client() as c:
            r = c.get(url)
            r.raise_for_status()
            return parse_feed(r.text, limit=limit)
