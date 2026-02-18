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
    Deterministic, cache-safe vectorization with:
      - incremental on-disk cache
      - intra-batch dedup (compute each unique text at most once per batch)

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

    # Keep original order for output
    texts: list[str] = []
    keys_ordered: list[VectorCacheKey] = []

    # Dedup inside batch by key
    unique_keys: list[VectorCacheKey] = []
    unique_texts: list[str] = []
    seen: set[str] = set()  # key filename is unique enough

    for inst in instances:
        t = _get_text(inst)
        k = VectorCacheKey(h=text_hash(t), version=version)
        texts.append(t)
        keys_ordered.append(k)

        k_id = k.filename()
        if k_id in seen:
            continue
        seen.add(k_id)
        unique_keys.append(k)
        unique_texts.append(t)

    # Load cache for unique keys
    vec_by_key: dict[str, np.ndarray] = {}
    hits = 0
    misses_keys: list[VectorCacheKey] = []
    misses_texts: list[str] = []

    for k, t in zip(unique_keys, unique_texts):
        v = cache.get(k)
        if v is not None:
            hits += 1
            vec_by_key[k.filename()] = v
        else:
            misses_keys.append(k)
            misses_texts.append(t)

    misses = len(misses_keys)

    # Compute only missing unique texts
    if misses_texts:
        X_missing = tfidf_vectorize(misses_texts, cfg=cfg)  # shape (m, d)
        for i, k in enumerate(misses_keys):
            vec = X_missing[i]
            cache.put(k, vec)
            vec_by_key[k.filename()] = vec

    dim = int(cfg.n_features)
    total_unique = len(unique_keys)
    total_items = len(keys_ordered)
    hit_rate = (float(hits) / float(total_unique)) if total_unique > 0 else 0.0
    dedup_ratio = (float(total_unique) / float(total_items)) if total_items > 0 else 1.0

    log.info(
        "vector_cache_stats hits=%s misses=%s hit_rate=%.3f dim=%s version=%s cache_dir=%s unique=%s total=%s dedup_ratio=%.3f",
        hits,
        misses,
        hit_rate,
        dim,
        version,
        cache_dir,
        total_unique,
        total_items,
        dedup_ratio,
    )
    emit_vector_cache_stats(
        hits=hits,
        misses=misses,
        dim=dim,
        unique_texts=total_unique,
        total_items=total_items,
    )

    # Reconstruct output matrix in original order
    filled = []
    for k in keys_ordered:
        v = vec_by_key.get(k.filename())
        if v is None:
            v = np.zeros(dim, dtype=np.float32)
        filled.append(v)

    X = np.stack(filled, axis=0).astype(np.float32, copy=False)
    return X
