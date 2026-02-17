from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import requests

from .rate_limit import RateLimiter


@dataclass
class HackerNewsClient:
    base_url: str = "https://hacker-news.firebaseio.com/v0"
    timeout_s: float = 10.0
    limiter: RateLimiter = field(default_factory=lambda: RateLimiter(min_interval_s=0.35))

    def _get_json(self, path: str) -> Optional[Any]:
        self.limiter.wait()
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        r = requests.get(url, timeout=self.timeout_s)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def get_item(self, item_id: int) -> Optional[dict[str, Any]]:
        payload = self._get_json(f"item/{item_id}.json")
        if payload is None:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def list_askstories(self) -> list[int]:
        payload = self._get_json("askstories.json")
        if not isinstance(payload, list):
            return []
        return [int(x) for x in payload]

    def list_showstories(self) -> list[int]:
        payload = self._get_json("showstories.json")
        if not isinstance(payload, list):
            return []
        return [int(x) for x in payload]
