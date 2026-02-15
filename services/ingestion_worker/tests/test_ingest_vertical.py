from ingestion_worker.pipeline import ingest_vertical as ingest_module


class DummyWriter:
    def __init__(self) -> None:
        self.seen = []

    def insert_many(self, signals):
        self.seen = signals
        return 2, 1


def test_ingest_vertical_returns_summary(monkeypatch):
    captured = {}

    def fake_fetch_reddit_signals(*, vertical_id: int, query: str, limit: int):
        captured["vertical_id"] = vertical_id
        captured["query"] = query
        captured["limit"] = limit
        return [
            {
                "vertical_id": vertical_id,
                "source": "reddit",
                "external_id": "a",
                "content": "hello",
                "url": "https://example.com/a",
                "created_at": None,
            },
            {
                "vertical_id": vertical_id,
                "source": "reddit",
                "external_id": "b",
                "content": "world",
                "url": "https://example.com/b",
                "created_at": None,
            },
        ]

    monkeypatch.setattr(ingest_module, "fetch_reddit_signals", fake_fetch_reddit_signals)
    monkeypatch.setattr(ingest_module, "SignalsWriter", lambda: DummyWriter())

    result = ingest_module.ingest_vertical(
        {
            "vertical_id": 1,
            "source": "reddit",
            "query": "saas",
            "limit": 10,
        }
    )

    assert captured == {"vertical_id": 1, "query": "saas", "limit": 10}
    assert result == {"fetched": 2, "inserted": 2, "skipped": 1}
