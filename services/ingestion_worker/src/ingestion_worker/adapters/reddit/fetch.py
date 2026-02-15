from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ingestion_worker.adapters.reddit.client import RedditClient
from ingestion_worker.adapters.reddit.map import map_post_to_signal
from ingestion_worker.adapters.reddit.types import RssItem
from ingestion_worker.adapters.reddit.rate_limit import RateLimiter


def _parse_created_at(value: object) -> Optional[datetime]:
    if value is None:
        return None
    try:
        ts = float(value)
    except (TypeError, ValueError):
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (OSError, OverflowError):
        return None


def fetch_reddit_signals(*, vertical_id: int, query: str, limit: int) -> List[dict]:
    """Fetch reddit signals for a vertical using a search query."""
    client = RedditClient()
    rate_limiter = RateLimiter()

    out: List[dict] = []  # Type correct pour la liste
    after = None

    while len(out) < limit:
        batch_size = min(25, limit - len(out))
        rate_limiter.acquire()

        posts, after = client.fetch_posts(query=query, limit=batch_size, after=after)
        if not posts:
            break

        for p in posts:
            if isinstance(p, dict):
                item = RssItem(
                    external_id=str(p.get("external_id") or p.get("id") or ""),
                    title=str(p.get("title") or ""),
                    content=str(p.get("content") or p.get("text") or p.get("title") or ""),
                    url=p.get("url"),
                    created_at_iso=_parse_created_at(p.get("created_at") or p.get("created_at_iso")),
                )
            else:
                item = p  # assume already RssItem-compatible

            out.append(map_post_to_signal(item, vertical_id=vertical_id, source="reddit"))
            if len(out) >= limit:
                break

        if after is None:
            break

    return out
