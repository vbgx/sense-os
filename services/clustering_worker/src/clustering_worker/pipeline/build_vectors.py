from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from clustering_worker.vectorize.cache.vector_cache import VectorCache, VectorCacheKey, text_hash
from clustering_worker.vectorize.tfidf import HashingVectorizerConfig, tfidf_vectorize, vectorizer_version


def _get_text(instance: Any) -> str:
    if isinstance(instance, dict):
        t = instance.get("text") or instance.get("content") or instance.get("body") or instance.get("title") or ""
        return str(t) if t is not None else ""
    # attribute style
    for attr in ("text", "content", "body", "title"):
        v = getattr(instance, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    v = getattr(instance, "text", None)
    return str(v) if v is not None else ""


def build_vectors(
    instances: Iterable[Any],
    *,
    cache_dir: str = ".cache/sense/vectors",
    cfg: HashingVectorizerConfig | None = None,
) -> np.ndarray:
    """
    Returns a dense float32 matrix of shape (n_instances, n_features).

    Cache strategy:
    - key = sha256(normalized_text) + vectorizer_version
    - store each vector as .npy (1D float32)
    - compute only misses, then reconstruct in original order
    """
    if cfg is None:
        cfg = HashingVectorizerConfig()

    version = vectorizer_version(cfg)
    cache = VectorCache(cache_dir)

    texts: list[str] = []
    keys: list[VectorCacheKey] = []
    cached: list[np.ndarray | None] = []

    for inst in instances:
        t = _get_text(inst)
        texts.append(t)
        k = VectorCacheKey(h=text_hash(t), version=version)
        keys.append(k)
        cached.append(cache.get(k))

    missing_idx = [i for i, v in enumerate(cached) if v is None]
    if missing_idx:
        missing_texts = [texts[i] for i in missing_idx]
        X_missing = tfidf_vectorize(missing_texts, cfg=cfg)  # shape (m, d)

        for j, i in enumerate(missing_idx):
            vec = X_missing[j]
            cache.put(keys[i], vec)
            cached[i] = vec

    # At this point all entries are filled
    filled = [v if v is not None else np.zeros(int(cfg.n_features), dtype=np.float32) for v in cached]
    X = np.stack(filled, axis=0).astype(np.float32, copy=False)
    return X
