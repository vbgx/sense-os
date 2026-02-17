from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


_CORE_FIELDS = (
    "type",
    "vertical_id",
    "vertical_db_id",
    "taxonomy_version",
    "day",
    "source",
    "run_id",
)


def _payload_hash(job: Dict[str, Any]) -> str:
    payload = {
        k: v
        for k, v in job.items()
        if k not in _CORE_FIELDS and not str(k).startswith("_")
    }
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def idempotency_key(job: Dict[str, Any]) -> str:
    """
    Deterministic key derived from:
    (job_type, vertical_id, vertical_db_id, taxonomy_version, day, source, run_id, payload_hash)
    """
    job_type = str(job.get("type") or "")
    vertical_id = str(job.get("vertical_id") or "")
    vertical_db_id = "" if job.get("vertical_db_id") is None else str(job.get("vertical_db_id"))
    taxonomy_version = str(job.get("taxonomy_version") or "")
    day = str(job.get("day") or "")
    source = str(job.get("source") or "")
    run_id = str(job.get("run_id") or "")
    payload_hash = _payload_hash(job)
    return f"{job_type}:{vertical_id}:{vertical_db_id}:{taxonomy_version}:{day}:{source}:{run_id}:{payload_hash}"
