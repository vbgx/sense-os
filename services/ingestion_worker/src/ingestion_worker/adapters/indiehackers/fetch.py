from __future__ import annotations

from typing import List, Dict
import feedparser


INDIEHACKERS_RSS_URL = "https://www.indiehackers.com/feed"


def fetch_indiehackers_rss(limit: int = 25) -> List[dict]:
    feed = feedparser.parse(INDIEHACKERS_RSS_URL)
    entries = feed.entries[:limit]

    out = []
    for entry in entries:
        out.append(
            {
                "guid": entry.get("id") or entry.get("link"),
                "title": entry.get("title") or "",
                "summary": entry.get("summary") or "",
                "link": entry.get("link"),
                "published": entry.get("published_parsed"),
            }
        )
    return out
