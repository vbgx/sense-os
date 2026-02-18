from __future__ import annotations

import hashlib


def sha256_text(t: str) -> str:
    s = " ".join((t or "").strip().split()).lower()
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
