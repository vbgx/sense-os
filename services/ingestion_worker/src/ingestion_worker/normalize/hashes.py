import hashlib

def sha256_text(text: str) -> str:
    if text is None:
        text = ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
