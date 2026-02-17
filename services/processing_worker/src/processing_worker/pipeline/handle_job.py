from __future__ import annotations

from typing import Any, Dict

from processing_worker.observability.logging import get_logger
from processing_worker.pipeline.process_batch import process_signals_batch

log = get_logger(__name__)


def handle_job(job: Dict[str, Any]) -> Dict[str, int]:
    """
    Standard worker entrypoint.

    Contract:
      - input: job dict
      - output: {"processed","created","skipped","errors"} ints

    Important:
      - Exceptions are logged here (with context) and re-raised so main() can fail the process.
    """
    vertical_db_id = job.get("vertical_db_id")
    job_id = job.get("job_id")

    try:
        res = process_signals_batch(job)

        processed = int(res.get("signals", 0))
        created = int(res.get("pain_instances_created", 0))
        skipped = int(res.get("pain_instances_skipped", 0))

        return {
            "processed": processed,
            "created": created,
            "skipped": skipped,
            "errors": 0,
        }
    except Exception:
        log.exception(
            "handle_job_failed",
            extra={
                "job_id": job_id,
                "vertical_db_id": vertical_db_id,
            },
        )
        # main() should fail (exit 1)
        raise
