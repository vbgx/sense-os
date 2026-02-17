from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import DEVTO_LIMITER
from .types import DevtoArticle


@dataclass
class DevtoClient:
    base_url: str = "https://dev.to/api/articles"
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
        limit: int = 30,
    ) -> Sequence[DevtoArticle]:

        params: dict[str, Any] = {
            "per_page": min(max(limit, 1), 100),
        }

        # DEV.to supports tag or search
        if " " not in query:
            params["tag"] = query
        else:
            params["search"] = query

        DEVTO_LIMITER.acquire()

        with self._client() as c:
            r = c.get(self.base_url, params=params)
            r.raise_for_status()
            data = r.json()

        out: list[DevtoArticle] = []
        for a in data:
            out.append(
                DevtoArticle(
                    id=a.get("id"),
                    title=a.get("title") or "",
                    description=a.get("description") or "",
                    url=a.get("url"),
                    published_at_iso=a.get("published_at"),
                    tags=(a.get("tag_list") or []),
                    author=(a.get("user") or {}).get("name"),
                    raw=a,
                )
            )

        return out
