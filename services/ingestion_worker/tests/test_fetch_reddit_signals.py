from datetime import datetime, timezone

from ingestion_worker.adapters.reddit import fetch as fetch_module


class DummyClient:
    last_instance = None

    def __init__(self) -> None:
        DummyClient.last_instance = self
        self.calls: list[tuple[str, int, str | None]] = []

    def fetch_posts(self, *, query: str, limit: int, after: str | None = None):
        self.calls.append((query, limit, after))
        if after is None:
            return [
                {
                    "external_id": "x1",
                    "title": "Title",
                    "content": "Content",
                    "url": "https://example.com/x1",
                    "created_at_iso": 1700000000,
                }
            ], "t3_after"
        return [], None


class DummyLimiter:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def acquire(self) -> None:
        return None


def test_fetch_reddit_signals_uses_query_and_maps(monkeypatch):
    monkeypatch.setattr(fetch_module, "RedditClient", DummyClient)
    monkeypatch.setattr(fetch_module, "RateLimiter", DummyLimiter)

    signals = fetch_module.fetch_reddit_signals(
        vertical_id="b2b_ops",
        vertical_db_id=1,
        taxonomy_version="2026-02-17",
        query="saas",
        limit=2,
    )

    assert DummyClient.last_instance is not None
    assert DummyClient.last_instance.calls[0][0] == "saas"
    assert signals[0]["vertical_id"] == "b2b_ops"
    assert signals[0]["vertical_db_id"] == 1
    assert signals[0]["taxonomy_version"] == "2026-02-17"
    assert signals[0]["source"] == "reddit"
    assert signals[0]["external_id"] == "x1"
    assert signals[0]["created_at"] == datetime.fromtimestamp(1700000000, tz=timezone.utc)
