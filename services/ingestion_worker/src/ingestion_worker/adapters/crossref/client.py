from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import CROSSREF_LIMITER
from .types import CrossrefWork


def _iso_from_parts(parts: Sequence[int] | None) -> str | None:
    """
    Crossref date-parts looks like [[YYYY, MM, DD]].
    We return ISO string (UTC) best-effort.
    """
    if not parts:
        return None
    try:
        y = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 1
        d = int(parts[2]) if len(parts) > 2 else 1
        dt = datetime(y, m, d, tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def _extract_published_iso(item: Mapping[str, Any]) -> str | None:
    for key in ("published-print", "published-online", "issued", "created", "deposited"):
        obj = item.get(key) or {}
        parts = None
        try:
            parts = (obj.get("date-parts") or [None])[0]
        except Exception:
            parts = None
        iso = _iso_from_parts(parts)
        if iso:
            return iso
    return None


def _extract_title(item: Mapping[str, Any]) -> str:
    t = item.get("title")
    if isinstance(t, list) and t:
        return str(t[0]).strip()
    if isinstance(t, str):
        return t.strip()
    return ""


def _extract_container(item: Mapping[str, Any]) -> str | None:
    ct = item.get("container-title")
    if isinstance(ct, list) and ct:
        return str(ct[0]).strip() or None
    if isinstance(ct, str):
        return ct.strip() or None
    return None


def _extract_authors(item: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for a in (item.get("author") or []) or []:
        if not isinstance(a, dict):
            continue
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        name = (given + " " + family).strip() or (a.get("name") or "").strip()
        if name:
            out.append(name)
    return out


@dataclass
class CrossrefClient:
    base_url: str = "https://api.crossref.org"
    timeout_s: float = 20.0

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
        rows: int = 50,
        sort: str = "relevance",
        order: str = "desc",
        filters: str | None = None,
    ) -> Sequence[CrossrefWork]:
        """
        Crossref works search.
        - filters example: "from-pub-date:2025-01-01,until-pub-date:2026-12-31"
        """
        rows = max(1, min(int(rows), 200))  # keep it polite; Crossref allows more but let's be safe

        params: dict[str, Any] = {
            "query": query,
            "rows": rows,
            "sort": sort,
            "order": order,
        }

        # Optional polite pool. Provide your email if you want.
        mailto = os.environ.get("CROSSREF_MAILTO")
        if mailto:
            params["mailto"] = mailto

        if filters:
            params["filter"] = filters

        url = f"{self.base_url}/works"

        CROSSREF_LIMITER.acquire()
        with self._client() as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        message = (data.get("message") or {}) if isinstance(data, dict) else {}
        items = (message.get("items") or []) if isinstance(message, dict) else []

        out: list[CrossrefWork] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            doi = (it.get("DOI") or it.get("doi") or "").strip()
            if not doi:
                continue

            out.append(
                CrossrefWork(
                    doi=doi,
                    title=_extract_title(it),
                    abstract=(it.get("abstract") or None),
                    published_at_iso=_extract_published_iso(it),
                    authors=_extract_authors(it),
                    container_title=_extract_container(it),
                    subjects=tuple((it.get("subject") or []) or []),
                    url=(it.get("URL") or it.get("url") or None),
                    raw=it,
                )
            )

        return out
