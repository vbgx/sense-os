from ingestion_worker.normalize.normalize_signal import normalize_reddit_item


def test_normalize_reddit_item_basic():
    s = normalize_reddit_item(
        guid="x",
        title="Title",
        summary="Summary",
        link="https://example.com",
        created_at=None,
    )
    assert s.source == "reddit"
    assert s.external_id == "x"
    assert "Title" in s.content
