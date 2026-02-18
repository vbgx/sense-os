import hashlib


def sha256_str(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
