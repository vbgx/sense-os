from __future__ import annotations

import logging
from typing import Any, Iterable

import numpy as np

from clustering_worker.vectorize.cache.vector_cache import VectorCache, VectorCacheKey, text_hash
from clustering_worker.vectorize.cache.metrics_emit import emit_vector_cache_stats
from clustering_worker.vectorize.tfidf import HashingVectorizerConfig, tfidf_vectorize, vectorizer_version
from clustering_worker.vectorize.vector_settings import get_vector_settings

log = logging.getLogger(__name__)


def _get_text(instance: Any) -> str:
    if isinstance(instance, dict):
        t = instance.get("text") or instance.get("content") or instance.get("body") or instance.get("title") or ""
        return str(t) if t is not None else ""
    for attr in ("text", "content", "body", "title"):
        v = getattr(instance, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    v = getattr(instance, "text", None)
    return str(v) if v is not None else ""


def build_vectors(
    instances: Iterable[Any],
    *,
    cache_dir: str | None = None,
    cfg: HashingVectorizerConfig | None = None,
) -> np.ndarray:
    """
    Deterministic, cache-safe vectorization.

    Env:
      - SENSE_VECTOR_CACHE_DIR (default: .cache/sense/vectors)
      - SENSE_VECTOR_N_FEATURES (default: 2**18)
      - SENSE_VECTOR_NGRAM_MAX (default: 2)
    """
    vs = get_vector_settings()

    if cache_dir is None:
        cache_dir = vs.cache_dir

    if cfg is None:
        cfg = HashingVectorizerConfig(
            n_features=int(vs.n_features),
            ngram_min=1,
            ngram_max=int(vs.ngram_max),
        )

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

    hits = sum(1 for v in cached if v is not None)
    missing_idx = [i for i, v in enumerate(cached) if v is None]
    misses = len(missing_idx)

    if missing_idx:
        missing_texts = [texts[i] for i in missing_idx]
        X_missing = tfidf_vectorize(missing_texts, cfg=cfg)  # shape (m, d)

        for j, i in enumerate(missing_idx):
            vec = X_missing[j]
            cache.put(keys[i], vec)
            cached[i] = vec

    dim = int(cfg.n_features)
    total = hits + misses
    hit_rate = (float(hits) / float(total)) if total > 0 else 0.0

    log.info(
        "vector_cache_stats hits=%s misses=%s hit_rate=%.3f dim=%s version=%s cache_dir=%s",
        hits,
        misses,
        hit_rate,
        dim,
        version,
        cache_dir,
    )
    emit_vector_cache_stats(hits=hits, misses=misses, dim=dim)

    filled = [v if v is not None else np.zeros(dim, dtype=np.float32) for v in cached]
    X = np.stack(filled, axis=0).astype(np.float32, copy=False)
    return X
