from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def idempotency_key(job: Dict[str, Any]) -> str:
    """
    Stable hash of the job payload (sorted keys).
    """
    s = json.dumps(job, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
