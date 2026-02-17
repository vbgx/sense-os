from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import HN_ALGOLIA_LIMITER
from .types import HackerNewsHit


@dataclass
class HackerNewsClient:
    """
    Uses HN Search powered by Algolia.
    - Search by date: https://hn.algolia.com/api/v1/search_by_date
    """
    base_url: str = "https://hn.algolia.com/api/v1"
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

    def search_by_date(
        self,
        *,
        query: str,
        hits_per_page: int = 50,
        tags: str = "story",
        page: int = 0,
    ) -> Sequence[HackerNewsHit]:
        """
        tags examples:
          - "story"
          - "ask_hn"
          - "show_hn"
          - "job"
          - "story,author_pg" etc (Algolia syntax)

        NOTE: We keep it simple: tags=story by default.
        """
        hits_per_page = max(1, min(int(hits_per_page), 100))
        page = max(0, int(page))

        url = f"{self.base_url}/search_by_date"
        params: dict[str, Any] = {
            "query": query,
            "tags": tags,
            "hitsPerPage": hits_per_page,
            "page": page,
        }

        HN_ALGOLIA_LIMITER.acquire()

        with self._client() as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        hits = data.get("hits") or []
        out: list[HackerNewsHit] = []

        for h in hits:
            if not isinstance(h, dict):
                continue

            obj_id = str(h.get("objectID") or "")
            if not obj_id:
                continue

            out.append(
                HackerNewsHit(
                    object_id=obj_id,
                    title=(h.get("title") or h.get("story_title") or "").strip(),
                    url=h.get("url") or h.get("story_url"),
                    author=h.get("author"),
                    points=int(h.get("points") or 0),
                    num_comments=int(h.get("num_comments") or 0),
                    created_at_iso=h.get("created_at") or "",
                    story_text=h.get("story_text"),
                    tags=tuple((h.get("_tags") or []) or []),
                    raw=h,
                )
            )

        return out
