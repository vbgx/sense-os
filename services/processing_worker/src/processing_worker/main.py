from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict

from sense_queue.client import RedisJobQueueClient
from sense_queue.worker_base import job_handler

from processing_worker.observability.logging import get_logger, safe_extra
from processing_worker.pipeline import handle_job as pipeline_handle_job

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


def _truthy_env(name: str, default: str = "0") -> bool:
    v = str(os.environ.get(name, default)).strip().lower()
    return v in {"1", "true", "yes", "y", "on"}


def _run_once(job: Dict[str, Any]) -> None:
    started = time.time()
    worker_name = "processing_worker"
    job_id = job.get("job_id")
    vertical_db_id = job.get("vertical_db_id")

    # Debug switch: when enabled, prints full JSON result.
    dump_json = _truthy_env("PROCESSING_DUMP_JSON", "0")

    try:
        res = pipeline_handle_job(job)
        took_ms = int((time.time() - started) * 1000)

        signals_n = int(res.get("loaded", 0))
        created_n = int(res.get("pain_instances_persisted", 0))
        updated_n = int(res.get("signals_updated", 0))

        log.info(
            "Processed vertical_id=%s signals=%s pain_instances_created=%s signals_updated=%s run_id=%s day=%s",
            job.get("vertical_id"),
            signals_n,
            created_n,
            updated_n,
            job.get("run_id"),
            job.get("day"),
        )

        log.info(
            "job_done",
            extra=safe_extra(
                {
                    "worker": worker_name,
                    "job_id": job_id,
                    "vertical_db_id": vertical_db_id,
                    "duration_ms": took_ms,
                    "items_processed": signals_n,
                    "items_created": created_n,
                    "items_updated": updated_n,
                }
            ),
        )

        # ✅ default: compact machine-readable (no gigantic payload)
        if dump_json:
            print(json.dumps({"ok": True, "result": res}))
        else:
            print(
                json.dumps(
                    {
                        "ok": True,
                        "result": {
                            "loaded": res.get("loaded", 0),
                            "envelopes": res.get("envelopes", 0),
                            "signals_updated": res.get("signals_updated", 0),
                            "pain_instances_persisted": res.get("pain_instances_persisted", 0),
                            "feature_metrics": res.get("feature_metrics", {}),
                        },
                    }
                )
            )

    except Exception:
        took_ms = int((time.time() - started) * 1000)
        log.exception(
            "job_failed",
            extra=safe_extra(
                {
                    "worker": worker_name,
                    "job_id": job_id,
                    "vertical_db_id": vertical_db_id,
                    "duration_ms": took_ms,
                }
            ),
        )
        print(json.dumps({"ok": False}))
        raise SystemExit(1)


@job_handler("process_signals")
def handle_process_signals(job: Dict[str, Any]) -> bool:
    _run_once(job)
    return True


def main() -> None:
    job = _load_job_from_env_or_stdin()
    if job:
        _run_once(job)
        return

    log.info("Processing worker booted")
    client = RedisJobQueueClient()
    client.run(queue="process")


if __name__ == "__main__":
    main()
