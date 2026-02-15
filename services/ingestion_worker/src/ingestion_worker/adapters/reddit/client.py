from __future__ import annotations
from dataclasses import dataclass, field
import json
import logging
from typing import Any, List, Tuple
from urllib.parse import urlencode, quote_plus

import requests

from ingestion_worker.adapters.reddit.rate_limit import RateLimiter

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class RedditClient:
    user_agent: str = "sense-os/0.1"
    timeout_s: float = 10.0
    limiter: RateLimiter = field(default_factory=RateLimiter)  # Corrected usage of default_factory

    def get(self, url: str) -> str:
        self.limiter.acquire()
        resp = requests.get(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json, application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.1",
            },
            timeout=self.timeout_s,
            allow_redirects=True,
        )

        ct = resp.headers.get("content-type", "")
        if resp.status_code >= 400:
            log.warning("reddit_get_failed status=%s url=%s content_type=%s body_prefix=%r", resp.status_code, url, ct, resp.text[:200])
            resp.raise_for_status()

        if "xml" not in ct and "rss" not in ct and "json" not in ct:
            log.warning("reddit_get_non_xml status=%s url=%s content_type=%s body_prefix=%r", resp.status_code, url, ct, resp.text[:200])

        return resp.text

    def fetch_posts(self, *, query: str, limit: int, after: str | None = None) -> Tuple[List[dict], str | None]:
        params = {
            "q": query,
            "sort": "top",
            "t": "day",
            "limit": str(limit),
        }
        if after:
            params["after"] = after

        url = f"https://www.reddit.com/search.json?{urlencode(params, quote_via=quote_plus)}"
        raw_data = self.get(url)
        data = self.parse_listing(raw_data)
        posts = self.parse_posts(data)
        after = self.get_next_cursor(data)
        return posts, after

    def parse_listing(self, raw_data: str) -> dict[str, Any]:
        try:
            return json.loads(raw_data)
        except json.JSONDecodeError:
            log.warning("reddit_parse_failed body_prefix=%r", raw_data[:200])
            return {}

    def parse_posts(self, data: dict[str, Any]) -> List[dict]:
        posts = []
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})
            posts.append({
                "external_id": post_data.get("id"),
                "title": post_data.get("title"),
                "content": post_data.get("selftext"),
                "url": post_data.get("url"),
                "created_at_iso": post_data.get("created_utc"),
            })
        return posts

    def get_next_cursor(self, data: dict[str, Any]) -> str | None:
        return data.get("data", {}).get("after")
