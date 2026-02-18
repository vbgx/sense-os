from __future__ import annotations

import os
from dataclasses import dataclass


def _int_env(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except Exception:
        return default


@dataclass(frozen=True)
class VectorSettings:
    cache_dir: str
    n_features: int
    ngram_max: int


def get_vector_settings() -> VectorSettings:
    return VectorSettings(
        cache_dir=os.environ.get("SENSE_VECTOR_CACHE_DIR", ".cache/sense/vectors"),
        n_features=_int_env("SENSE_VECTOR_N_FEATURES", 2**18),
        ngram_max=_int_env("SENSE_VECTOR_NGRAM_MAX", 2),
    )
