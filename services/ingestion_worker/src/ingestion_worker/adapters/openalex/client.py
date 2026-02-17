from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import OPENALEX_LIMITER
from .types import OpenAlexWork


def _inv_index_to_abstract(inv: Mapping[str, Any] | None) -> str | None:
    """
    OpenAlex abstracts come as 'abstract_inverted_index' (word -> [positions]).
    We reconstruct best-effort. If missing, return None.
    """
    if not inv or not isinstance(inv, dict):
        return None

    positions: dict[int, str] = {}
    for word, pos_list in inv.items():
        if not isinstance(word, str) or not isinstance(pos_list, list):
            continue
        for p in pos_list:
            try:
                positions[int(p)] = word
            except Exception:
                continue

    if not positions:
        return None

    out = []
    for i in sorted(positions.keys()):
        out.append(positions[i])
    return " ".join(out).strip() or None


def _extract_authors(item: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for a in (item.get("authorships") or []) or []:
        if not isinstance(a, dict):
            continue
        author = a.get("author") or {}
        name = (author.get("display_name") or "").strip()
        if name:
            out.append(name)
    return out


def _extract_concepts(item: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for c in (item.get("concepts") or []) or []:
        if not isinstance(c, dict):
            continue
        name = (c.get("display_name") or "").strip()
        if name:
            out.append(name)
    return out


def _host_venue(item: Mapping[str, Any]) -> str | None:
    hv = item.get("host_venue") or {}
    if isinstance(hv, dict):
        name = (hv.get("display_name") or "").strip()
        return name or None
    return None


@dataclass
class OpenAlexClient:
    base_url: str = "https://api.openalex.org"
    timeout_s: float = 25.0

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": settings.sense_ua,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )

    def search_works(
        self,
        *,
        query: str,
        per_page: int = 50,
        sort: str = "relevance_score:desc",
    ) -> Sequence[OpenAlexWork]:
        per_page = max(1, min(int(per_page), 200))

        params: dict[str, Any] = {
            "search": query,
            "per-page": per_page,
            "sort": sort,
        }

        mailto = os.environ.get("OPENALEX_MAILTO")
        if mailto:
            params["mailto"] = mailto

        url = f"{self.base_url}/works"

        OPENALEX_LIMITER.acquire()
        with self._client() as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        results = (data.get("results") or []) if isinstance(data, dict) else []

        out: list[OpenAlexWork] = []
        for it in results:
            if not isinstance(it, dict):
                continue

            wid = (it.get("id") or "").strip()
            if not wid:
                continue

            abstract = _inv_index_to_abstract(it.get("abstract_inverted_index"))
            authors = _extract_authors(it)
            concepts = _extract_concepts(it)
            doi = it.get("doi")

            out.append(
                OpenAlexWork(
                    id=wid,
                    doi=doi,
                    title=(it.get("display_name") or "").strip(),
                    abstract=abstract,
                    published_at=it.get("publication_date"),
                    updated_at=it.get("updated_date"),
                    authors=tuple(authors),
                    host_venue=_host_venue(it),
                    cited_by_count=int(it.get("cited_by_count") or 0),
                    concepts=tuple(concepts[:20]),
                    url=it.get("primary_location", {}).get("landing_page_url") if isinstance(it.get("primary_location"), dict) else None,
                    raw=it,
                )
            )

        return out
