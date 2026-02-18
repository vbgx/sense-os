from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

try:
    from sklearn.feature_extraction.text import HashingVectorizer
except Exception as e:  # pragma: no cover
    HashingVectorizer = None  # type: ignore[assignment]
    _SKLEARN_IMPORT_ERROR = e
else:
    _SKLEARN_IMPORT_ERROR = None


@dataclass(frozen=True)
class HashingVectorizerConfig:
    """
    Cache-safe vectorization: fixed dimensionality, independent per text.
    Note: this is not classic TF-IDF (no corpus-dependent IDF), but it's deterministic
    and works great for similarity + clustering at scale.
    """
    n_features: int = 2**18  # 262k dims (tune later)
    ngram_min: int = 1
    ngram_max: int = 2
    alternate_sign: bool = False
    norm: str = "l2"  # important for cosine similarity / clustering stability
    lowercase: bool = True


def vectorizer_version(cfg: HashingVectorizerConfig) -> str:
    return (
        f"hashvec_v1__nf={cfg.n_features}__ng={cfg.ngram_min}-{cfg.ngram_max}"
        f"__as={int(cfg.alternate_sign)}__norm={cfg.norm}__lc={int(cfg.lowercase)}"
    )


def tfidf_vectorize(texts: Iterable[str], *, cfg: HashingVectorizerConfig | None = None) -> np.ndarray:
    if cfg is None:
        cfg = HashingVectorizerConfig()

    if HashingVectorizer is None:  # pragma: no cover
        raise RuntimeError(f"scikit-learn is required for vectorization: {_SKLEARN_IMPORT_ERROR}")

    vec = HashingVectorizer(
        n_features=int(cfg.n_features),
        ngram_range=(int(cfg.ngram_min), int(cfg.ngram_max)),
        alternate_sign=bool(cfg.alternate_sign),
        norm=str(cfg.norm),
        lowercase=bool(cfg.lowercase),
    )

    texts_list = [t or "" for t in texts]
    X = vec.transform(texts_list)  # scipy sparse
    # convert to dense float32 (your clustering code likely expects dense)
    return X.astype(np.float32).toarray()
