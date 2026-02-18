from __future__ import annotations

from typing import Sequence, Optional

import httpx

from ingestion_worker.settings import settings
from .rate_limit import STACKEXCHANGE_LIMITER
from .types import StackExchangeQuestion


class StackExchangeClient:
    base_url: str = "https://api.stackexchange.com/2.3"
    default_site: str = "stackoverflow"
    timeout_s: float = 20.0

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": settings.sense_ua,
                "Accept": "application/json",
            },
        )

    def search_questions(
        self,
        *,
        query: str,
        limit: int,
        cursor: Optional[str] = None,
        site: Optional[str] = None,
    ) -> Sequence[StackExchangeQuestion]:
        """
        Uses /search/advanced endpoint.

        cursor -> page number (1-based)
        """

        page = 1
        if cursor:
            try:
                page = max(1, int(cursor))
            except Exception:
                page = 1

        per_page = max(1, min(limit, 100))

        params = {
            "order": "desc",
            "sort": "activity",
            "q": query,
            "site": site or self.default_site,
            "page": page,
            "pagesize": per_page,
            "filter": "default",
        }

        url = f"{self.base_url}/search/advanced"

        STACKEXCHANGE_LIMITER.acquire()

        with self._client() as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        items = data.get("items", []) if isinstance(data, dict) else []

        out: list[StackExchangeQuestion] = []

        for item in items:
            owner = item.get("owner") or {}

            out.append(
                StackExchangeQuestion(
                    question_id=item.get("question_id"),
                    title=item.get("title") or "",
                    link=item.get("link"),
                    creation_date=item.get("creation_date"),
                    last_activity_date=item.get("last_activity_date"),
                    score=item.get("score") or 0,
                    answer_count=item.get("answer_count") or 0,
                    view_count=item.get("view_count") or 0,
                    is_answered=item.get("is_answered") or False,
                    tags=item.get("tags") or [],
                    owner_display_name=owner.get("display_name"),
                    raw=item,
                )
            )

        return out
