import httpx


def build_http_client(
    user_agent: str,
    timeout: float = 10.0,
    max_retries: int = 3,
) -> httpx.Client:
    transport = httpx.HTTPTransport(retries=max_retries)

    return httpx.Client(
        headers={"User-Agent": user_agent},
        timeout=timeout,
        transport=transport,
    )
