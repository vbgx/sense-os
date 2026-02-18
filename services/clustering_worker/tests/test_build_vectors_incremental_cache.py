from __future__ import annotations

from pathlib import Path

import numpy as np

from clustering_worker.pipeline.build_vectors import build_vectors
from clustering_worker.vectorize.tfidf import HashingVectorizerConfig


def test_build_vectors_cache_warm_skips_recompute(tmp_path: Path, monkeypatch):
    cfg = HashingVectorizerConfig(n_features=2**12)  # smaller for test speed
    cache_dir = tmp_path / "vectors"

    instances = [{"text": "Hello world"}, {"text": "Hello world"}, {"text": "Different text"}]

    # cold run: populates cache
    X1 = build_vectors(instances, cache_dir=str(cache_dir), cfg=cfg)
    assert isinstance(X1, np.ndarray)
    assert X1.shape[0] == 3

    calls = {"n": 0}
    from clustering_worker import vectorize as _  # noqa: F401
    from clustering_worker.vectorize import tfidf as tfidf_mod

    real = tfidf_mod.tfidf_vectorize

    def wrapped(texts, *, cfg=None):
        calls["n"] += len(list(texts))
        return real(texts, cfg=cfg)

    monkeypatch.setattr(tfidf_mod, "tfidf_vectorize", wrapped)

    # warm run: should hit cache for all three (only 2 unique texts, but both should be cached)
    X2 = build_vectors(instances, cache_dir=str(cache_dir), cfg=cfg)
    assert X2.shape == X1.shape
    assert calls["n"] == 0
