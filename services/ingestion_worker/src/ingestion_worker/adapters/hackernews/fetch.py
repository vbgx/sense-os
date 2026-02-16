from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .client import HackerNewsClient
from .types import HNItem, parse_hn_item


@dataclass(frozen=True)
class HNFetchConfig:
    max_stories: int = 50
    max_comments_per_story: int = 30


def fetch_story_ids(client: HackerNewsClient, kind: str) -> list[int]:
    if kind == "ask":
        return client.list_askstories()
    if kind == "show":
        return client.list_showstories()
    raise ValueError(f"Unsupported HN kind: {kind}")


def fetch_stories(
    client: HackerNewsClient,
    *,
    kind: str,
    cfg: HNFetchConfig,
) -> list[tuple[HNItem, dict]]:
    ids = fetch_story_ids(client, kind)[: cfg.max_stories]
    out: list[tuple[HNItem, dict]] = []
    for story_id in ids:
        raw = client.get_item(story_id)
        if raw is None:
            continue
        item = parse_hn_item(raw)
        if item.type != "story":
            continue
        out.append((item, raw))
    return out


def iter_comments_flat(
    client: HackerNewsClient,
    *,
    story: HNItem,
    cfg: HNFetchConfig,
) -> Iterable[tuple[HNItem, dict]]:
    count = 0
    queue = list(story.kids or [])
    while queue and count < cfg.max_comments_per_story:
        cid = queue.pop(0)
        raw = client.get_item(cid)
        if raw is None:
            continue
        item = parse_hn_item(raw)
        if item.type != "comment":
            continue
        yield (item, raw)
        count += 1
