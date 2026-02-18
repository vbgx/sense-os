from __future__ import annotations

from typing import Any

from ingestion_worker.adapters._base import Adapter
from ingestion_worker.adapters.hackernews.adapter import HackerNewsAdapter
from ingestion_worker.adapters.reddit.adapter import RedditAdapter

_REGISTRY: dict[str, Any] = {
    "reddit": RedditAdapter,
    "hackernews": HackerNewsAdapter,
}


def get_adapter(source: str) -> Adapter:
    key = str(source).strip().lower()
    if key not in _REGISTRY:
        raise ValueError(f"unknown source: {source}")
    return _REGISTRY[key]()
