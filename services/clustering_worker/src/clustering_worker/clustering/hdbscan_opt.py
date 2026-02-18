from __future__ import annotations

from typing import Any

import numpy as np


def optimize_hdbscan_params(vectors, *, min_cluster_size_min: int = 4) -> dict[str, Any]:
    n = int(getattr(vectors, "shape", [0])[0] or 0)
    if n <= 0:
        return {"min_cluster_size": min_cluster_size_min, "min_samples": 2, "metric": "euclidean"}

    mcs = max(min_cluster_size_min, int(np.clip(n * 0.03, min_cluster_size_min, 30)))
    ms = max(2, min(10, int(mcs / 2)))

    return {
        "min_cluster_size": int(mcs),
        "min_samples": int(ms),
        "metric": "euclidean",
    }
