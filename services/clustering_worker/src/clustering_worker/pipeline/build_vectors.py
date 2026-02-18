from __future__ import annotations

import logging
import time
from typing import Any, Iterable

import numpy as np

from clustering_worker.vectorize.cache.vector_cache import VectorCache, VectorCacheKey, text_hash
from clustering_worker.vectorize.cache.metrics_emit import emit_vector_cache_stats
from clustering_worker.vectorize.cache.json_log import log_json
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
      - JSON log event for dashboards (vectorize_stats)

    Env:
      - SENSE_VECTOR_CACHE_DIR (default: .cache/sense/vectors)
      - SENSE_VECTOR_N_FEATURES (default: 2**18)
      - SENSE_VECTOR_NGRAM_MAX (default: 2)
    """
    t0 = time.perf_counter()

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
    keys_ordered: list[VectorCacheKey] = []

    # Dedup inside batch by key
    unique_keys: list[VectorCacheKey] = []
    unique_texts: list[str] = []
    seen: set[str] = set()

    total_items = 0
    for inst in instances:
        total_items += 1
        t = _get_text(inst)
        k = VectorCacheKey(h=text_hash(t), version=version)
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
    compute_ms = 0.0
    if misses_texts:
        t_compute = time.perf_counter()
        X_missing = tfidf_vectorize(misses_texts, cfg=cfg)
        compute_ms = (time.perf_counter() - t_compute) * 1000.0

        for i, k in enumerate(misses_keys):
            vec = X_missing[i]
            cache.put(k, vec)
            vec_by_key[k.filename()] = vec

    dim = int(cfg.n_features)
    total_unique = len(unique_keys)
    hit_rate = (float(hits) / float(total_unique)) if total_unique > 0 else 0.0
    dedup_ratio = (float(total_unique) / float(total_items)) if total_items > 0 else 1.0

    # Human-readable log
    log.info(
        "vector_cache_stats hits=%s misses=%s hit_rate=%.3f dim=%s version=%s cache_dir=%s unique=%s total=%s dedup_ratio=%.3f compute_ms=%.1f",
        hits,
        misses,
        hit_rate,
        dim,
        version,
        cache_dir,
        total_unique,
        total_items,
        dedup_ratio,
        compute_ms,
    )

    # JSON log (single line)
    total_ms = (time.perf_counter() - t0) * 1000.0
    log_json(
        log,
        "vectorize_stats",
        {
            "cache_dir": str(cache_dir),
            "version": str(version),
            "dim": int(dim),
            "items_total": int(total_items),
            "texts_unique": int(total_unique),
            "dedup_ratio": float(dedup_ratio),
            "cache_hits": int(hits),
            "cache_misses": int(misses),
            "cache_hit_rate": float(hit_rate),
            "compute_ms": float(compute_ms),
            "total_ms": float(total_ms),
        },
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
