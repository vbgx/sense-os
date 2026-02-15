from ingestion_worker.normalize.hashes import sha256_text

def compute_content_hash(content: str) -> str:
    return sha256_text(content or "")
