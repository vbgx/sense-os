from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


def _hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hash_vec(text: str, *, dim: int = 256) -> np.ndarray:
    v = np.zeros((dim,), dtype=float)
    for tok in text.lower().split():
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        v[h % dim] += 1.0
    n = float(np.linalg.norm(v))
    if n > 0:
        v = v / n
    return v


def build_vectors(job: dict[str, Any], instances: list[dict[str, Any]], *, cache_dir: str | None = None) -> tuple[list[int], np.ndarray, dict[str, Any]]:
    cache_path = Path(cache_dir) if cache_dir else None
    if cache_path:
        cache_path.mkdir(parents=True, exist_ok=True)

    ids: list[int] = []
    vecs: list[np.ndarray] = []
    recomputed = 0
    reused = 0

    for inst in instances:
        iid = int(inst.get("id") or inst.get("instance_id") or inst.get("pain_instance_id") or 0)
        text = str(inst.get("text") or inst.get("body") or inst.get("title") or "")
        ids.append(iid)

        th = _hash_text(text)
        if cache_path:
            fp = cache_path / f"{iid}.npz"
            if fp.exists():
                try:
                    data = np.load(fp, allow_pickle=False)
                    if str(data["text_hash"]) == th:
                        vecs.append(np.asarray(data["vec"], dtype=float))
                        reused += 1
                        continue
                except Exception:
                    pass

        v = _hash_vec(text)
        vecs.append(v)
        recomputed += 1
        if cache_path:
            fp = cache_path / f"{iid}.npz"
            np.savez_compressed(fp, vec=v, text_hash=np.array(th))

    X = np.vstack(vecs) if vecs else np.zeros((0, 256), dtype=float)

    if bool(job.get("emit_json_event")):
        print(
            json.dumps(
                {
                    "event": "vectorize",
                    "n_instances": len(ids),
                    "recomputed": recomputed,
                    "reused": reused,
                }
            )
        )

    meta = {"recomputed": recomputed, "reused": reused, "dim": int(X.shape[1]) if X.ndim == 2 else 0}
    return ids, X, meta
