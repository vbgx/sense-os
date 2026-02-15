from ingestion_worker.normalize.hashes import sha256_text


def test_sha256_text_stable():
    assert sha256_text("abc") == sha256_text("abc")
