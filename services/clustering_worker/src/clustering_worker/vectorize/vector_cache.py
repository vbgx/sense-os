from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
from scipy import sparse


@dataclass(frozen=True)
class VectorCacheKey:
    vertical_db_id: int
    taxonomy_version: str
    algo: str = "tfidf_v1"


class VectorCache:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)

    def _dir(self, key: VectorCacheKey) -> Path:
        return self.base_dir / key.algo / f"vertical={key.vertical_db_id}" / f"tax={key.taxonomy_version}"

    def _meta_path(self, key: VectorCacheKey) -> Path:
        return self._dir(key) / "meta.json"

    def _vectors_path(self, key: VectorCacheKey) -> Path:
        return self._dir(key) / "vectors.npz"

    def _model_path(self, key: VectorCacheKey) -> Path:
        return self._dir(key) / "model.joblib"

    def load_if_fresh(self, key: VectorCacheKey, expected_meta: dict[str, Any]):
        meta_path = self._meta_path(key)
        vectors_path = self._vectors_path(key)
        model_path = self._model_path(key)

        if not meta_path.exists() or not vectors_path.exists() or not model_path.exists():
            return None

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta != expected_meta:
            return None

        vectors = sparse.load_npz(vectors_path)
        model = joblib.load(model_path)
        return model, vectors

    def save(self, key: VectorCacheKey, meta: dict[str, Any], model, vectors) -> None:
        out_dir = self._dir(key)
        out_dir.mkdir(parents=True, exist_ok=True)

        self._meta_path(key).write_text(json.dumps(meta, sort_keys=True), encoding="utf-8")
        sparse.save_npz(self._vectors_path(key), vectors)
        joblib.dump(model, self._model_path(key))
