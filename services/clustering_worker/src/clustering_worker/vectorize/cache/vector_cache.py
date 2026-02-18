from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


def _normalize_text(t: str) -> str:
    return " ".join((t or "").strip().split()).lower()


def text_hash(text: str) -> str:
    n = _normalize_text(text)
    return hashlib.sha256(n.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class VectorCacheKey:
    h: str
    version: str

    def filename(self) -> str:
        return f"{self.version}__{self.h}.npy"


class VectorCache:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, key: VectorCacheKey) -> Optional[np.ndarray]:
        p = self.root / key.filename()
        if not p.exists():
            return None
        try:
            arr = np.load(p)
            if arr.ndim != 1:
                return None
            return arr.astype(np.float32, copy=False)
        except Exception:
            return None

    def put(self, key: VectorCacheKey, vec: np.ndarray) -> None:
        p = self.root / key.filename()
        tmp = p.with_suffix(".tmp.npy")
        np.save(tmp, vec.astype(np.float32, copy=False))
        tmp.replace(p)
