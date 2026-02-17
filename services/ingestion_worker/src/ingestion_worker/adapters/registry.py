from __future__ import annotations

from typing import Callable, Dict

from ingestion_worker.adapters._base import Adapter

from ingestion_worker.adapters.crossref import CrossrefAdapter
from ingestion_worker.adapters.devto import DevtoAdapter
from ingestion_worker.adapters.gdelt import GdeltAdapter
from ingestion_worker.adapters.github import GithubAdapter
from ingestion_worker.adapters.googlenews import GoogleNewsAdapter
from ingestion_worker.adapters.hackernews import HackerNewsAdapter
from ingestion_worker.adapters.lobsters import LobstersAdapter
from ingestion_worker.adapters.mastodon import MastodonAdapter
from ingestion_worker.adapters.openalex import OpenAlexAdapter
from ingestion_worker.adapters.stackexchange import StackExchangeAdapter
from ingestion_worker.adapters.wikipedia import WikipediaAdapter

# Optional/legacy sources (keep commented until standardized)
# from ingestion_worker.adapters.arxiv import ArxivAdapter

AdapterFactory = Callable[[], Adapter]

ADAPTERS: Dict[str, AdapterFactory] = {
    "crossref": CrossrefAdapter,
    "devto": DevtoAdapter,
    "gdelt": GdeltAdapter,
    "github": GithubAdapter,
    "googlenews": GoogleNewsAdapter,
    "hackernews": HackerNewsAdapter,
    "lobsters": LobstersAdapter,
    "mastodon": MastodonAdapter,
    "openalex": OpenAlexAdapter,
    "stackexchange": StackExchangeAdapter,
    "wikipedia": WikipediaAdapter,
    # "arxiv": ArxivAdapter,
}


def get_adapter(name: str) -> Adapter:
    key = (name or "").strip().lower()
    if key not in ADAPTERS:
        raise KeyError(f"Unknown adapter: {name}. Known: {sorted(ADAPTERS.keys())}")
    return ADAPTERS[key]()
