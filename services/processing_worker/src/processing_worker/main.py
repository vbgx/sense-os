from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict

from processing_worker.observability.logging import get_logger, safe_extra
from processing_worker.pipeline import handle_job

log = get_logger(__name__)


def _load_job_from_env_or_stdin() -> Dict[str, Any]:
    """
    Minimal, deterministic job loader.

    Priority:
      1) JOB_JSON env var
      2) stdin JSON (single object)
      3) fallback empty dict
    """
    raw = os.environ.get("JOB_JSON")
    if raw:
        return json.loads(raw)

    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            return json.loads(data)

    return {}


def main() -> None:
    started = time.time()
    job = _load_job_from_env_or_stdin()

    worker_name = "processing_worker"
    job_id = job.get("job_id")
    vertical_db_id = job.get("vertical_db_id")

    try:
        res = handle_job(job)
        took_ms = int((time.time() - started) * 1000)

        log_res = {
            "items_processed": int(res.get("processed", 0)),
            "items_created": int(res.get("created", 0)),
            "items_skipped": int(res.get("skipped", 0)),
            "items_errors": int(res.get("errors", 0)),
        }

        log.info(
            "job_done",
            extra=safe_extra({
                "worker": worker_name,
                "job_id": job_id,
                "vertical_db_id": vertical_db_id,
                "duration_ms": took_ms,
                **log_res,
            }),
        )

        # output machine-readable for scripts
        print(json.dumps({"ok": True, "result": res}))
        if int(res.get("errors", 0)) > 0:
            raise SystemExit(1)

    except Exception:
        took_ms = int((time.time() - started) * 1000)
        log.exception(
            "job_failed",
            extra=safe_extra({
                "worker": worker_name,
                "job_id": job_id,
                "vertical_db_id": vertical_db_id,
                "duration_ms": took_ms,
            }),
        )
        print(json.dumps({"ok": False}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
