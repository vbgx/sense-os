from __future__ import annotations

import httpx


def build_http_client(
    *,
    user_agent: str,
    timeout_s: float = 20.0,
    max_retries: int = 2,
) -> httpx.Client:
    transport = httpx.HTTPTransport(retries=max_retries)
    return httpx.Client(
        transport=transport,
        timeout=httpx.Timeout(timeout_s),
        headers={"User-Agent": user_agent},
        follow_redirects=True,
    )
