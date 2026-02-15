from __future__ import annotations

from dataclasses import dataclass

import feedparser

from ingestion_worker.adapters.reddit.client import RedditClient


@dataclass(frozen=True)
class RssItem:
    guid: str
    title: str
    summary: str
    link: str
    published: str | None = None


def fetch_rss_items(feed_url: str, client: RedditClient) -> list[RssItem]:
    xml = client.get(feed_url)
    parsed = feedparser.parse(xml)
    items: list[RssItem] = []
    for e in parsed.entries:
        guid = getattr(e, "id", None) or getattr(e, "guid", None) or getattr(e, "link", None) or ""
        title = getattr(e, "title", "") or ""
        summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
        link = getattr(e, "link", "") or ""
        published = getattr(e, "published", None)
        if guid and link:
            items.append(RssItem(guid=guid, title=title, summary=summary, link=link, published=published))
    return items
