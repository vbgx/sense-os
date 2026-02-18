from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable

from ingestion_worker.adapters._base import Adapter


@dataclass(frozen=True, slots=True)
class AdapterSpec:
    source: str
    factory: Callable[[], Adapter]


def _canon(source: str) -> str:
    return str(source).strip().lower()


_REGISTRY: Dict[str, AdapterSpec] = {}


def _try_register(source: str, import_path: str, class_name: str) -> None:
    """
    Best-effort adapter registration.

    Any import error (missing adapter.py, wrong class name, missing deps) should NOT
    prevent the ingestion worker from starting. It simply makes that source unavailable.
    """
    key = _canon(source)
    try:
        mod = __import__(import_path, fromlist=[class_name])
        cls = getattr(mod, class_name)
    except Exception:
        return

    _REGISTRY[key] = AdapterSpec(source=key, factory=cls)


# --- Register known sources (only those that import cleanly will appear in list_sources()) ---
_try_register("reddit", "ingestion_worker.adapters.reddit.adapter", "RedditAdapter")
_try_register("hackernews", "ingestion_worker.adapters.hackernews.adapter", "HackerNewsAdapter")
_try_register("indiehackers", "ingestion_worker.adapters.indiehackers.adapter", "IndieHackersAdapter")
_try_register("producthunt", "ingestion_worker.adapters.producthunt.adapter", "ProductHuntAdapter")
_try_register("lobsters", "ingestion_worker.adapters.lobsters.adapter", "LobstersAdapter")
_try_register("rss", "ingestion_worker.adapters.rss.adapter", "RssAdapter")
_try_register("googlenews", "ingestion_worker.adapters.googlenews.adapter", "GoogleNewsAdapter")
_try_register("wikipedia", "ingestion_worker.adapters.wikipedia.adapter", "WikipediaAdapter")
_try_register("stackexchange", "ingestion_worker.adapters.stackexchange.adapter", "StackExchangeAdapter")
_try_register("openalex", "ingestion_worker.adapters.openalex.adapter", "OpenAlexAdapter")
_try_register("crossref", "ingestion_worker.adapters.crossref.adapter", "CrossrefAdapter")
_try_register("arxiv", "ingestion_worker.adapters.arxiv.adapter", "ArxivAdapter")
_try_register("devto", "ingestion_worker.adapters.devto.adapter", "DevtoAdapter")
_try_register("gdelt", "ingestion_worker.adapters.gdelt.adapter", "GdeltAdapter")
_try_register("mastodon", "ingestion_worker.adapters.mastodon.adapter", "MastodonAdapter")

# ✅ GitHub (class name is GithubAdapter in your code)
_try_register("github", "ingestion_worker.adapters.github.adapter", "GithubAdapter")


def list_sources() -> list[str]:
    return sorted(_REGISTRY.keys())


def has_source(source: str) -> bool:
    return _canon(source) in _REGISTRY


def require_supported_sources(sources: Iterable[str]) -> None:
    bad = [s for s in sources if not has_source(s)]
    if bad:
        supported = ", ".join(list_sources())
        bad_s = ", ".join(repr(b) for b in bad)
        raise ValueError(
            f"unknown or unavailable sources: [{bad_s}]. supported: [{supported}]"
        )


def get_adapter(source: str) -> Adapter:
    key = _canon(source)
    spec = _REGISTRY.get(key)
    if spec is None:
        supported = ", ".join(list_sources())
        raise ValueError(
            f"unknown or unavailable source: {source!r}. supported: [{supported}]"
        )
    return spec.factory()
