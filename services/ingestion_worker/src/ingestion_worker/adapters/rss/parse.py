from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Optional

from .types import RssItem


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return (el.text or "").strip()


def _find_text(parent: ET.Element, tag: str, ns: dict[str, str] | None = None) -> str:
    el = parent.find(tag, ns or {})
    return _text(el)


def _atom_link(entry: ET.Element, ns: dict[str, str]) -> str:
    # Prefer rel="alternate"
    for link in entry.findall("atom:link", ns):
        rel = link.attrib.get("rel", "")
        href = link.attrib.get("href", "")
        if rel == "alternate" and href:
            return href
    # fallback
    link = entry.find("atom:link", ns)
    if link is not None:
        return link.attrib.get("href", "") or ""
    return ""


def _looks_like_html(s: str) -> bool:
    t = (s or "").lstrip().lower()
    # common anti-bot / error payloads
    return t.startswith("<!doctype html") or t.startswith("<html") or t.startswith("<head") or t.startswith("<body")


def parse_feed(xml_content: str, *, limit: int = 100) -> list[RssItem]:
    """
    Parse RSS2 or Atom to RssItem list.
    NEVER raise: on invalid feeds, return [].
    """
    if not xml_content:
        return []
    if _looks_like_html(xml_content):
        return []

    try:
        root = ET.fromstring(xml_content)
    except Exception:
        return []

    # Atom
    if root.tag.endswith("feed"):
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items: list[RssItem] = []
        for entry in root.findall("atom:entry", ns):
            _id = _find_text(entry, "atom:id", ns) or _atom_link(entry, ns)
            title = _find_text(entry, "atom:title", ns)
            link = _atom_link(entry, ns)
            content = _find_text(entry, "atom:content", ns) or _find_text(entry, "atom:summary", ns)
            published = _find_text(entry, "atom:published", ns) or _find_text(entry, "atom:updated", ns)
            author = ""
            a = entry.find("atom:author", ns)
            if a is not None:
                author = _find_text(a, "atom:name", ns)

            if not link:
                continue

            items.append(
                RssItem(
                    id=_id or link,
                    title=title or link,
                    link=link,
                    content=content or "",
                    published_at=published or None,
                    author=author or None,
                    raw={"format": "atom"},
                )
            )
            if len(items) >= limit:
                break
        return items

    # RSS 2.0
    channel = root.find("channel")
    if channel is None:
        channel = root.find("./channel")

    items: list[RssItem] = []
    if channel is None:
        return items

    for it in channel.findall("item"):
        guid = _find_text(it, "guid")
        link = _find_text(it, "link")
        title = _find_text(it, "title")

        desc = _find_text(it, "description")
        content_encoded = ""
        for child in list(it):
            if child.tag.endswith("encoded"):
                content_encoded = (child.text or "").strip()
                break
        content = content_encoded or desc

        pub = _find_text(it, "pubDate") or _find_text(it, "date")
        author = _find_text(it, "author")

        if not link:
            continue

        items.append(
            RssItem(
                id=guid or link,
                title=title or link,
                link=link,
                content=content or "",
                published_at=pub or None,
                author=author or None,
                raw={"format": "rss2"},
            )
        )
        if len(items) >= limit:
            break

    return items
