from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence
from urllib.parse import quote
import time

import httpx

from .rate_limit import MEDIAWIKI_ACTION_LIMITER, WIKIMEDIA_REST_LIMITER
from .types import WikipediaPageView, WikipediaRecentChange


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _date_yyyymmdd00(dt: datetime) -> str:
    return dt.strftime("%Y%m%d00")


def _parse_retry_after_s(v: str | None) -> float | None:
    if not v:
        return None
    v = v.strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


@dataclass
class WikipediaClient:
    rest_base_url: str = "https://wikimedia.org/api/rest_v1"
    api_base_url: str = "https://en.wikipedia.org/w/api.php"

    project: str = "en.wikipedia.org"
    access: str = "all-access"
    agent: str = "user"
    granularity: str = "daily"

    timeout_s: float = 15.0
    user_agent: str = "sense-os/0.1 (ingestion_worker; contact: you@example.com)"

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        )

    def _get_json(
        self,
        *,
        url: str,
        params: Mapping[str, Any] | None,
        limiter: Any,
        max_retries: int = 5,
        base_backoff_s: float = 1.0,
        backoff_cap_s: float = 60.0,
    ) -> Mapping[str, Any]:
        with self._client() as c:
            for attempt in range(max_retries + 1):
                limiter.acquire()

                r = c.get(url, params=params)
                if r.status_code in (403, 429, 503):
                    retry_after = _parse_retry_after_s(r.headers.get("Retry-After"))
                    backoff = min(backoff_cap_s, retry_after if retry_after is not None else base_backoff_s * (2**attempt))

                    # Wikimedia bot traffic message -> back off harder
                    body_text = ""
                    try:
                        body_text = r.text or ""
                    except Exception:
                        body_text = ""
                    if r.status_code == 403 and "bot-traffic@wikimedia.org" in body_text:
                        backoff = max(backoff, 30.0)

                    if attempt >= max_retries:
                        r.raise_for_status()

                    time.sleep(backoff)
                    continue

                r.raise_for_status()
                data = r.json()
                if isinstance(data, dict):
                    return data
                return {"data": data}

        raise RuntimeError("Unreachable")

    # -----------------------
    # Pageviews (REST)
    # -----------------------
    def fetch_pageviews(self, *, article: str, limit: int = 30) -> Sequence[WikipediaPageView]:
        days = max(1, int(limit))
        end = _utc_now()
        start = end - timedelta(days=days)

        article_path = quote(article, safe="")
        url = (
            f"{self.rest_base_url}/metrics/pageviews/per-article/"
            f"{self.project}/{self.access}/{self.agent}/"
            f"{article_path}/{self.granularity}/"
            f"{_date_yyyymmdd00(start)}/{_date_yyyymmdd00(end)}"
        )

        data = self._get_json(url=url, params=None, limiter=WIKIMEDIA_REST_LIMITER)

        items = data.get("items", []) or []
        out: list[WikipediaPageView] = []
        for it in items:
            ts = it.get("timestamp")
            views = it.get("views", 0)
            art = it.get("article") or article

            if isinstance(ts, str) and len(ts) >= 10:
                yyyy, mm, dd, hh = ts[0:4], ts[4:6], ts[6:8], ts[8:10]
                timestamp_iso = f"{yyyy}-{mm}-{dd}T{hh}:00:00Z"
            else:
                timestamp_iso = _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")

            out.append(WikipediaPageView(article=art, views=int(views or 0), timestamp_iso=timestamp_iso, raw=it))
        return out

    # -----------------------
    # Search (Action API)
    # -----------------------
    def search_titles(self, *, query: str, limit: int = 10) -> Sequence[str]:
        """
        Real search via MediaWiki list=search.
        Returns page titles (namespace 0 only).
        """
        q = (query or "").strip()
        if not q:
            return []

        params: dict[str, Any] = {
            "action": "query",
            "list": "search",
            "srsearch": q,
            "srlimit": min(50, max(1, int(limit))),
            "srnamespace": 0,  # articles only
            "format": "json",
        }

        payload = self._get_json(url=self.api_base_url, params=params, limiter=MEDIAWIKI_ACTION_LIMITER, backoff_cap_s=30.0)

        results = (((payload.get("query") or {}).get("search")) or [])
        titles: list[str] = []
        for r in results:
            t = r.get("title")
            if t:
                titles.append(str(t))
        return titles

    # -----------------------
    # Recent changes (Action API)
    # -----------------------
    def fetch_recent_changes_for_title(self, *, title: str, limit: int = 50, hours: int = 168) -> Sequence[WikipediaRecentChange]:
        """
        Fetch recent changes restricted to a given title (server-side filter).
        hours default = 7 days.
        """
        want = max(1, int(limit))
        chunk = min(50, max(10, want))

        now = _utc_now()
        start = now
        end = now - timedelta(hours=max(1, int(hours)))

        params_base: dict[str, Any] = {
            "action": "query",
            "list": "recentchanges",
            "rcprop": "title|ids|timestamp|user|comment",
            "rclimit": chunk,
            "rcdir": "older",
            "rcnamespace": 0,
            "rctitle": title,  # key bit: server-side filter
            "rcstart": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rcend": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "format": "json",
        }

        out: list[WikipediaRecentChange] = []
        cont: Mapping[str, Any] | None = None

        # small loop; title-filtered so should converge fast
        for _ in range(6):
            params = dict(params_base)
            if cont:
                params.update(cont)

            payload = self._get_json(url=self.api_base_url, params=params, limiter=MEDIAWIKI_ACTION_LIMITER, backoff_cap_s=30.0)

            rc = (((payload.get("query") or {}).get("recentchanges")) or [])
            for it in rc:
                pageid = it.get("pageid") or it.get("page_id") or 0
                user = it.get("user")
                comment = it.get("comment")
                ts = it.get("timestamp") or _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")

                out.append(
                    WikipediaRecentChange(
                        page_id=int(pageid or 0),
                        title=title,
                        user=user,
                        comment=comment,
                        timestamp_iso=ts,
                        raw=it,
                    )
                )
                if len(out) >= want:
                    return out

            cont_obj = payload.get("continue")
            if not cont_obj:
                break
            cont = cont_obj

        return out

    def fetch_recent_changes(self, *, query: str, limit: int = 50) -> Sequence[WikipediaRecentChange]:
        """
        Realistic "recent changes for query":
          - search titles
          - fetch recent changes for those titles
          - aggregate until limit
        """
        want = max(1, int(limit))
        titles = self.search_titles(query=query, limit=min(10, want))
        if not titles:
            return []

        out: list[WikipediaRecentChange] = []
        for t in titles:
            # Pull a few per title; total capped by want
            remaining = want - len(out)
            if remaining <= 0:
                break
            per_title = min(10, remaining)
            out.extend(self.fetch_recent_changes_for_title(title=t, limit=per_title, hours=168))

        return out
