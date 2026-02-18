from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import GDELT_LIMITER
from .types import GdeltArticle


@dataclass
class GdeltClient:
    base_url: str = "https://api.gdeltproject.org/api/v2/doc/doc"
    timeout_s: float = 20.0

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": settings.sense_ua,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )

    def search(
        self,
        *,
        query: str,
        max_records: int = 50,
        timespan: str = "7d",
    ) -> Sequence[GdeltArticle]:

        params = {
            "query": query,
            "mode": "ArtList",
            "maxrecords": max_records,
            "timespan": timespan,
            "format": "json",
        }

        GDELT_LIMITER.acquire()

        with self._client() as c:
            r = c.get(self.base_url, params=params)
            r.raise_for_status()
            data = r.json()

        articles = data.get("articles") or []

        out: list[GdeltArticle] = []
        for a in articles:
            if not isinstance(a, dict):
                continue

            out.append(
                GdeltArticle(
                    url=a.get("url"),
                    title=a.get("title") or "",
                    source_country=a.get("sourcecountry"),
                    language=a.get("language"),
                    published_at_iso=a.get("seendate"),
                    domain=a.get("domain"),
                    raw=a,
                )
            )

        return out
