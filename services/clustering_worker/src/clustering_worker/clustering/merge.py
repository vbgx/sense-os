from __future__ import annotations

from typing import Any

import numpy as np


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def cluster_vectors(vectors, *, params: dict[str, Any] | None = None) -> list[int]:
    params = params or {}
    thr = float(params.get("similarity_threshold", 0.82))

    X = np.asarray(vectors, dtype=float)
    n = int(X.shape[0])
    labels = [-1] * n
    cluster_id = 0

    for i in range(n):
        if labels[i] != -1:
            continue
        labels[i] = cluster_id
        for j in range(i + 1, n):
            if labels[j] != -1:
                continue
            if _cosine_sim(X[i], X[j]) >= thr:
                labels[j] = cluster_id
        cluster_id += 1

    return labels
