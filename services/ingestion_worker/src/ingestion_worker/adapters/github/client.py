from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Sequence

import httpx

from ingestion_worker.settings import settings
from .rate_limit import GITHUB_LIMITER
from .types import GithubIssue


def _sleep_until_reset(headers: dict[str, str]) -> None:
    reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    if not reset:
        return
    try:
        reset_ts = int(reset)
        now = int(time.time())
        if reset_ts > now:
            time.sleep(min(60.0, float(reset_ts - now) + 1.0))
    except Exception:
        return


@dataclass
class GithubClient:
    base_url: str = "https://api.github.com"
    timeout_s: float = 20.0

    def _headers(self) -> dict[str, str]:
        headers = {
            "User-Agent": settings.sense_ua,
            "Accept": "application/vnd.github+json",
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers=self._headers(),
            follow_redirects=True,
        )

    def search_issues(self, *, query: str, per_page: int = 50) -> Sequence[GithubIssue]:
        q = f"{query} type:issue in:title,body"

        params: dict[str, Any] = {
            "q": q,
            "per_page": min(max(per_page, 1), 100),
            "sort": "updated",
            "order": "desc",
        }

        url = f"{self.base_url}/search/issues"

        GITHUB_LIMITER.acquire()

        with self._client() as c:
            r = c.get(url, params=params)

            if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
                _sleep_until_reset(r.headers)
                GITHUB_LIMITER.acquire()
                r = c.get(url, params=params)

            r.raise_for_status()
            data = r.json()

        items = data.get("items", []) if isinstance(data, dict) else []

        out: list[GithubIssue] = []

        for it in items:
            repo_url = it.get("repository_url", "")
            repo_full_name = ""
            if "/repos/" in repo_url:
                repo_full_name = repo_url.split("/repos/")[1]

            labels = [l["name"] for l in it.get("labels", []) if isinstance(l, dict) and l.get("name")]

            out.append(
                GithubIssue(
                    id=it.get("id"),
                    number=it.get("number"),
                    title=it.get("title") or "",
                    body=it.get("body") or "",
                    html_url=it.get("html_url"),
                    repo_full_name=repo_full_name,
                    state=it.get("state"),
                    created_at=it.get("created_at"),
                    updated_at=it.get("updated_at"),
                    author=(it.get("user") or {}).get("login"),
                    labels=labels,
                    raw=it,
                )
            )

        return out
