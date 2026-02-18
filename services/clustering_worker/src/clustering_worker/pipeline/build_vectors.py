from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from clustering_worker.vectorize.tfidf import HashingVectorizerConfig, tfidf_vectorize, vectorizer_version


def _hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _coerce_text(inst: dict[str, Any]) -> str:
    return str(inst.get("text") or inst.get("body") or inst.get("title") or inst.get("content") or "")


def _coerce_id(inst: dict[str, Any], *, fallback: int) -> int:
    return int(inst.get("id") or inst.get("instance_id") or inst.get("pain_instance_id") or fallback)


def _cache_subdir(cache_path: Path, *, cfg: HashingVectorizerConfig) -> Path:
    subdir = cache_path / vectorizer_version(cfg)
    subdir.mkdir(parents=True, exist_ok=True)
    return subdir


def build_vectors(
    job_or_instances: dict[str, Any] | list[dict[str, Any]],
    instances: list[dict[str, Any]] | None = None,
    *,
    cache_dir: str | None = None,
    cfg: HashingVectorizerConfig | None = None,
) -> tuple[list[int], np.ndarray, dict[str, Any]] | np.ndarray:
    return_only_X = False
    if instances is None and isinstance(job_or_instances, list):
        instances = job_or_instances
        job: dict[str, Any] = {}
        return_only_X = True
    else:
        job = job_or_instances if isinstance(job_or_instances, dict) else {}
        instances = instances or []

    if cfg is None:
        cfg = HashingVectorizerConfig()

    cache_path = Path(cache_dir) if cache_dir else None
    cache_subdir = _cache_subdir(cache_path, cfg=cfg) if cache_path else None

    texts = [_coerce_text(inst) for inst in instances]
    ids = [_coerce_id(inst, fallback=idx + 1) for idx, inst in enumerate(instances)]

    unique_texts: list[str] = []
    seen: set[str] = set()
    for text in texts:
        if text not in seen:
            seen.add(text)
            unique_texts.append(text)

    cached: dict[str, np.ndarray] = {}
    recomputed = 0
    reused = 0

    if cache_subdir:
        for text in unique_texts:
            th = _hash_text(text)
            fp = cache_subdir / f"{th}.npz"
            if not fp.exists():
                continue
            try:
                data = np.load(fp, allow_pickle=False)
                cached[text] = np.asarray(data["vec"], dtype=float)
                reused += 1
            except Exception:
                continue

    missing_texts = [text for text in unique_texts if text not in cached]
    if missing_texts:
        computed = tfidf_vectorize(missing_texts, cfg=cfg)
        for text, vec in zip(missing_texts, computed, strict=False):
            cached[text] = np.asarray(vec, dtype=float)
        recomputed = len(missing_texts)
        if cache_subdir:
            for text in missing_texts:
                th = _hash_text(text)
                fp = cache_subdir / f"{th}.npz"
                np.savez_compressed(fp, vec=cached[text])

    vecs = [cached[text] for text in texts]
    X = np.vstack(vecs) if vecs else np.zeros((0, int(cfg.n_features)), dtype=float)

    emit_json_event = bool(job.get("emit_json_event")) if not return_only_X else True
    if emit_json_event:
        payload = {
            "event": "vectorize_stats",
            "items_total": len(texts),
            "texts_unique": len(unique_texts),
            "recomputed": recomputed,
            "reused": reused,
            "vectorizer_version": vectorizer_version(cfg),
        }
        import logging

        logging.getLogger(__name__).info(json.dumps(payload))

    meta = {"recomputed": recomputed, "reused": reused, "dim": int(X.shape[1]) if X.ndim == 2 else 0}
    if return_only_X:
        return X
    return ids, X, meta
