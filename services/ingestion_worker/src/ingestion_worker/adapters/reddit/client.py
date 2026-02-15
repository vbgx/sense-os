from __future__ import annotations
from dataclasses import dataclass, field
import logging
import requests
from typing import List, Tuple
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
                "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.1",
            },
            timeout=self.timeout_s,
            allow_redirects=True,
        )

        ct = resp.headers.get("content-type", "")
        if resp.status_code >= 400:
            log.warning("reddit_get_failed status=%s url=%s content_type=%s body_prefix=%r", resp.status_code, url, ct, resp.text[:200])
            resp.raise_for_status()

        if "xml" not in ct and "rss" not in ct:
            log.warning("reddit_get_non_xml status=%s url=%s content_type=%s body_prefix=%r", resp.status_code, url, ct, resp.text[:200])

        return resp.text

    def fetch_posts(self, vertical_id: int, limit: int, after: str | None = None) -> Tuple[List[dict], str | None]:
        url = f"https://www.reddit.com/r/{vertical_id}/top/.json?limit={limit}&after={after}"
        raw_data = self.get(url)
        posts = self.parse_posts(raw_data)  # Parse posts based on the structure of the response
        after = self.get_next_cursor(raw_data)
        return posts, after

    def parse_posts(self, raw_data: str) -> List[dict]:
        data = requests.get(raw_data).json()
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

    def get_next_cursor(self, raw_data: str) -> str | None:
        data = requests.get(raw_data).json()
        return data.get("data", {}).get("after")
