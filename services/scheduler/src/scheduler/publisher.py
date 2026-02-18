from __future__ import annotations

import logging
import time
from typing import Any, Iterable

from sense_queue.client import RedisJobQueueClient
from scheduler.jobs import asdict

log = logging.getLogger(__name__)


def _emoji_for_job(job_type: str | None) -> str:
    t = (job_type or "").strip()
    if t == "ingest_vertical":
        return "🧲"
    if t == "process_signals":
        return "🧠"
    if t == "cluster_vertical":
        return "🧩"
    if t == "trend_day":
        return "📈"
    return "📦"


def _compact(v: Any, *, max_len: int = 90) -> str:
    if v is None:
        return "-"
    s = str(v)
    s = " ".join(s.split())
    if len(s) > max_len:
        return s[: max_len - 1] + "…"
    return s


def _sources_summary(payload: dict[str, Any]) -> tuple[int, str]:
    sources = payload.get("sources") or []
    if isinstance(sources, list):
        clean = [str(x).strip() for x in sources if str(x).strip()]
        n = len(clean)
        if n == 0:
            return 0, "-"
        if n <= 6:
            return n, ",".join(clean)
        return n, ",".join(clean[:6]) + ",…"
    return 0, "-"


def _job_one_liner(payload: dict[str, Any]) -> str:
    t = payload.get("type")
    q = payload.get("queue")
    rid = payload.get("run_id")
    vid = payload.get("vertical_id")
    vdb = payload.get("vertical_db_id")
    day = payload.get("day")

    src = payload.get("source")
    sources_n, sources_short = _sources_summary(payload)

    query = payload.get("query")
    limit = payload.get("limit")
    offset = payload.get("offset")

    emo = _emoji_for_job(str(t) if t is not None else None)

    # make the important bits impossible to miss
    return (
        f"{emo} enqueue "
        f"type={_compact(t)} → queue={_compact(q)} "
        f"| vertical={_compact(vid)} (db={_compact(vdb)}) day={_compact(day)} "
        f"| run_id={_compact(rid)} "
        f"| source={_compact(src)} sources={sources_n}[{_compact(sources_short)}] "
        f"| query={_compact(query)} limit={_compact(limit)} offset={_compact(offset)}"
    )


def publish_jobs(jobs: Iterable[Any]) -> int:
    """
    Publish jobs to Redis queues.

    This log line is the ground truth of what was enqueued.
    If you can't understand the run from logs → this function failed its job.
    """
    client = RedisJobQueueClient()
    n = 0
    t0 = time.perf_counter()

    # Tiny morale boost. Not too much noise.
    log.info("🚀 publisher start (jobs=?)")

    for j in jobs:
        payload = asdict(j)
        queue = payload.get("queue")
        if not isinstance(queue, str) or not queue:
            raise ValueError(f"Job missing queue: {payload!r}")

        log.info("%s", _job_one_liner(payload))
        client.publish(queue, payload)
        n += 1

    dt = time.perf_counter() - t0
    if n == 0:
        log.warning("🤨 publisher done (published=0) — no jobs were provided")
    else:
        log.info("✅ publisher done published_jobs=%s seconds=%.3f", n, dt)

    return n
