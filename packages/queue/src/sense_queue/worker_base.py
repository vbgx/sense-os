from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

log = logging.getLogger(__name__)

JobDict = Dict[str, Any]
Handler = Callable[[JobDict], None]

HANDLERS: Dict[str, Handler] = {}


def job_handler(job_type: str) -> Callable[[Handler], Handler]:
    def _decorator(fn: Handler) -> Handler:
        if job_type in HANDLERS:
            raise RuntimeError(f"Duplicate handler for job type {job_type!r}")
        HANDLERS[job_type] = fn
        return fn
    return _decorator


def get_handler(job_type: str) -> Optional[Handler]:
    return HANDLERS.get(job_type)


def handle_job(job: JobDict) -> bool:
    jt = job.get("type")
    if not jt or not isinstance(jt, str):
        log.warning("Skip invalid job (missing type): %r", job)
        return False

    fn = get_handler(jt)
    if not fn:
        log.warning("Skip unknown job: %r", job)
        return False

    fn(job)
    return True
