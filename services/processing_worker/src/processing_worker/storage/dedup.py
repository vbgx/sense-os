"""
Processing dedup policy (V1):
- Idempotency key = algo_version + breakdown_hash.
- DB uniqueness enforces (algo_version, breakdown_hash).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _normalize_breakdown(breakdown: Any) -> str:
    """
    Return a stable JSON string for hashing.
    """
    payload = {} if breakdown is None else breakdown
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def breakdown_hash(breakdown: Any) -> str:
    """
    Compute a stable hash of the breakdown payload.
    """
    normalized = _normalize_breakdown(breakdown)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def idempotency_key(algo_version: str, breakdown: Any) -> str:
    """
    Idempotency key derived from algo_version and breakdown.
    """
    return f"{algo_version}:{breakdown_hash(breakdown)}"
