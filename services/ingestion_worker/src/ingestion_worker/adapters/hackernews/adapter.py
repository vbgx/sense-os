from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from ingestion_worker.adapters.hackernews.client import HackerNewsClient
from ingestion_worker.adapters.hackernews.fetch import HNFetchConfig, fetch_stories, iter_comments_flat
from ingestion_worker.adapters.hackernews.map import map_hn_comment_to_signal_dict, map_hn_story_to_signal_dict


@dataclass(frozen=True)
class HNAdapterConfig:
    kinds: tuple[str, ...] = ("ask", "show")
    max_stories: int = 50
    max_comments_per_story: int = 30


def ingest_hackernews(
    *,
    client: HackerNewsClient,
    vertical_id: str,
    vertical_db_id: int | None,
    taxonomy_version: str | None,
    cfg: HNAdapterConfig,
) -> Iterable[Dict[str, Any]]:
    fetch_cfg = HNFetchConfig(
        max_stories=cfg.max_stories,
        max_comments_per_story=cfg.max_comments_per_story,
    )

    for kind in cfg.kinds:
        for story, raw_story in fetch_stories(client, kind=kind, cfg=fetch_cfg):
            yield map_hn_story_to_signal_dict(
                story,
                raw_story,
                vertical_id=vertical_id,
                vertical_db_id=vertical_db_id,
                taxonomy_version=taxonomy_version,
                kind=kind,
            )

            for comment, raw_comment in iter_comments_flat(client, story=story, cfg=fetch_cfg):
                yield map_hn_comment_to_signal_dict(
                    comment,
                    raw_comment,
                    vertical_id=vertical_id,
                    vertical_db_id=vertical_db_id,
                    taxonomy_version=taxonomy_version,
                    parent_story_id=story.id,
                )
