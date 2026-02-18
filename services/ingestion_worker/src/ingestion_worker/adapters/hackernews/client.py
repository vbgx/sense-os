from __future__ import annotations

import httpx

from ingestion_worker.settings import settings


class HackerNewsClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            timeout=settings.http_timeout_s,
            headers={"User-Agent": settings.user_agent},
        )

    def get_item(self, item_id: int) -> dict:
        r = self._client.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
        r.raise_for_status()
        return r.json()

    def close(self) -> None:
        self._client.close()
