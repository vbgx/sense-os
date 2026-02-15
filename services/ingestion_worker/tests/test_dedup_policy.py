from ingestion_worker.storage.dedup import compute_content_hash


def test_compute_content_hash_stable():
    assert compute_content_hash("hello") == compute_content_hash("hello")
