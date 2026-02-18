from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Sequence

from ingestion_worker.adapters.rss.client import RssClient
from ingestion_worker.adapters.rss.types import RssItem


DEFAULT_RSS_URL = os.getenv("INDIEHACKERS_RSS_URL", "https://www.indiehackers.com/feed")


@dataclass
class IndieHackersClient:
    rss_url: str = DEFAULT_RSS_URL
    timeout_s: float = 20.0

    def fetch_recent(self, *, limit: int = 50) -> Sequence[RssItem]:
        client = RssClient(timeout_s=self.timeout_s)
        return client.fetch_feed(url=self.rss_url, limit=limit)
