from __future__ import annotations

import argparse
import logging
import time
from datetime import date, timedelta
from typing import Optional, Callable

from sqlalchemy import text

from db.session import SessionLocal
from scheduler.checkpoints import (
    ensure_checkpoint,
    get_checkpoint,
    mark_checkpoint_complete,
    mark_checkpoint_progress,
    next_day_to_run,
    seed_checkpoint,
)
from scheduler.planner import plan_vertical_run
from scheduler.publisher import publish_jobs
from scheduler.run_id import new_run_id

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("scheduler")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sense OS scheduler")
    p.add_argument("--vertical-id", type=int, default=1)
    p.add_argument("--source", type=str, default="reddit")
    p.add_argument("--mode", type=str, choices=["once", "backfill"], default="once")

    p.add_argument("--query", type=str, default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--offset", type=int, default=None)

    p.add_argument("--days", type=int, default=90, help="Backfill window size (days)")
    p.add_argument("--start", type=str, default=None, help="YYYY-MM-DD (optional)")
    p.add_argument("--end", type=str, default=None, help="YYYY-MM-DD (optional, inclusive)")
    p.add_argument("--series", dest="series", action="store_true", help="Run 7d then 90d backfill")
    p.add_argument("--no-series", dest="series", action="store_false", help="Run a single backfill window")
    p.set_defaults(series=True)
    return p.parse_args()


def _parse_day(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def _default_day() -> date:
    # for backfill default window; "once" will infer day from DB after ingest
    return date.today() - timedelta(days=1)


def _scalar(sql: str, params: Optional[dict[str, object]] = None):
    db = SessionLocal()
    try:
        return db.execute(text(sql), params or {}).scalar_one()
    finally:
        db.close()


def _scalar_int(sql: str, params: Optional[dict[str, object]] = None) -> int:
    return int(_scalar(sql, params))


def _emit_metric(name: str, value: float | int, **tags: object) -> None:
    """
    Emit a structured metric line for logs.
    """
    tag_s = " ".join(f"{k}={v}" for k, v in tags.items())
    if tag_s:
        log.info("metric %s=%s %s", name, value, tag_s)
    else:
        log.info("metric %s=%s", name, value)


def _wait_count_ge(
    label: str,
    sql: str,
    params: Optional[dict[str, object]],
    expected: int,
    timeout_s: int = 90,
) -> int:
    """
    Wait until a SQL count reaches or exceeds a threshold.
    """
    t0 = time.time()
    last = 0
    while time.time() - t0 < timeout_s:
        try:
            last = _scalar_int(sql, params)
        except Exception:
            last = 0
        if last >= expected:
            log.info("wait_ok label=%s count=%s", label, last)
            return last
        # show progress occasionally so it doesn't feel "stuck"
        if int(time.time() - t0) % 5 == 0:
            log.info("wait_progress label=%s last=%s expected>=%s", label, last, expected)
        time.sleep(1)
    raise SystemExit(
        f"timeout waiting for {label}: expected>={expected} last={last} sql={sql!r} params={params!r}"
    )


def _infer_latest_signal_day(vertical_id: int) -> date:
    v = _scalar(
        "select max(ingested_at)::date from signals where vertical_id=:vertical_id",
        {"vertical_id": vertical_id},
    )
    if v is None:
        raise SystemExit("could not infer day from signals (no signals ingested)")
    # scalar_one returns a Python date already (psycopg)
    return v


def _run_day_sequential(
    *,
    vertical_id: int,
    source: str,
    d: date,
    run_id: str,
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
) -> None:
    """
    Deterministic orchestration for a single (vertical_id, day):
    ingest -> wait signals(day) -> process -> wait pain_instances(day) -> cluster -> wait cluster_signals -> trend -> wait daily_metrics(day)

    NOTE: run_id is provided by caller (single run_id propagated).
    """
    day_s = d.isoformat()
    day_start = d.isoformat()
    next_day = (d + timedelta(days=1)).isoformat()
    log.info("run_day vertical_id=%s day=%s run_id=%s", vertical_id, day_s, run_id)
    day_timer_start = time.perf_counter()

    jobs = plan_vertical_run(
        vertical_id=vertical_id,
        source=source,
        run_id=run_id,
        day=d,
        query=query,
        limit=limit,
        offset=offset,
    )
    ingest, process, cluster, trend = jobs

    stage_start = time.perf_counter()
    publish_jobs([ingest])
    signals_n = _wait_count_ge(
        "signals(day)",
        """
        select count(*)
        from signals
        where vertical_id=:vertical_id
          and ingested_at >= :day_start
          and ingested_at < :day_end
        """.strip(),
        {"vertical_id": vertical_id, "day_start": day_start, "day_end": next_day},
        1,
        timeout_s=90,
    )
    _emit_metric("signals_count", signals_n, vertical_id=vertical_id, day=day_s, stage="ingest")
    _emit_metric("stage_seconds", time.perf_counter() - stage_start, vertical_id=vertical_id, day=day_s, stage="ingest")

    stage_start = time.perf_counter()
    publish_jobs([process])
    pains_n = _wait_count_ge(
        "pain_instances(day)",
        """
        select count(*)
        from pain_instances
        where vertical_id=:vertical_id
          and created_at >= :day_start
          and created_at < :day_end
        """.strip(),
        {"vertical_id": vertical_id, "day_start": day_start, "day_end": next_day},
        1,
        timeout_s=90,
    )
    _emit_metric("pain_instances_count", pains_n, vertical_id=vertical_id, day=day_s, stage="process")
    _emit_metric("stage_seconds", time.perf_counter() - stage_start, vertical_id=vertical_id, day=day_s, stage="process")

    stage_start = time.perf_counter()
    publish_jobs([cluster])
    cluster_links_n = _wait_count_ge(
        "cluster_signals",
        """
        select count(*)
        from cluster_signals cs
        join pain_instances pi on pi.id = cs.pain_instance_id
        where pi.vertical_id=:vertical_id
        """.strip(),
        {"vertical_id": vertical_id},
        1,
        timeout_s=90,
    )
    _emit_metric("cluster_signals_count", cluster_links_n, vertical_id=vertical_id, day=day_s, stage="cluster")
    _emit_metric("stage_seconds", time.perf_counter() - stage_start, vertical_id=vertical_id, day=day_s, stage="cluster")

    stage_start = time.perf_counter()
    publish_jobs([trend])
    try:
        metrics_n = _wait_count_ge(
            "cluster_daily_metrics(day)",
            "select count(*) from cluster_daily_metrics where day >= CAST(:day_start AS date) and day < CAST(:day_end AS date)",
            {"day_start": day_start, "day_end": next_day},
            1,
            timeout_s=90,
        )
    except SystemExit as exc:
        # Trend computation can legitimately return 0 rows for small datasets.
        # Do not fail the whole scheduler run; allow validate to continue.
        log.warning("trend_metrics_timeout day=%s vertical_id=%s err=%s", day_s, vertical_id, exc)
        metrics_n = 0
    _emit_metric("daily_metrics_count", metrics_n, vertical_id=vertical_id, day=day_s, stage="trend")
    _emit_metric("stage_seconds", time.perf_counter() - stage_start, vertical_id=vertical_id, day=day_s, stage="trend")
    _emit_metric("day_seconds", time.perf_counter() - day_timer_start, vertical_id=vertical_id, day=day_s)


def _run_once_infer_day_then_sequential(
    *,
    vertical_id: int,
    source: str,
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
) -> None:
    """
    Durable 'once' with SINGLE run_id:
    1) generate run_id ONCE
    2) publish ingest without assuming any day (day=None) using that run_id
    3) wait signals exist
    4) infer actual day from signals.max(ingested_at)::date
    5) publish process/cluster/trend for that day using SAME run_id
    """
    run_id = new_run_id()
    log.info(
        "once_publish_ingest run_id=%s vertical_id=%s source=%s",
        run_id,
        vertical_id,
        source,
    )

    # publish ingest only (day=None) with SAME run_id
    jobs = plan_vertical_run(
        vertical_id=vertical_id,
        source=source,
        run_id=run_id,
        day=None,
        query=query,
        limit=limit,
        offset=offset,
    )
    ingest = jobs[0]
    publish_jobs([ingest])

    _wait_count_ge(
        "signals(any)",
        "select count(*) from signals where vertical_id=:vertical_id",
        {"vertical_id": vertical_id},
        1,
        timeout_s=90,
    )

    d = _infer_latest_signal_day(vertical_id)
    log.info("once_inferred_day day=%s run_id=%s", d.isoformat(), run_id)

    # run process/cluster/trend for inferred day with SAME run_id
    _run_day_sequential(
        vertical_id=vertical_id,
        source=source,
        d=d,
        run_id=run_id,
        query=query,
        limit=limit,
        offset=offset,
    )


def _resolve_backfill_bounds(
    *,
    days: int,
    start: Optional[date],
    end: Optional[date],
) -> tuple[date, date]:
    """
    Resolve backfill start/end bounds.
    """
    if start and end:
        if end < start:
            raise SystemExit("end must be >= start")
        return start, end
    if start or end:
        raise SystemExit("start and end must be provided together")

    day1 = _default_day()
    day0 = day1 - timedelta(days=int(days) - 1)
    return day0, day1


def _run_backfill_window(
    *,
    name: str,
    vertical_id: int,
    source: str,
    days: int,
    start: Optional[date],
    end: Optional[date],
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    seed_last_completed_day: Optional[date] = None,
    run_day_fn: Callable[..., None] = _run_day_sequential,
) -> None:
    """
    Run a backfill window with checkpointing and crash recovery.
    """
    start_day, end_day = _resolve_backfill_bounds(days=days, start=start, end=end)

    state = ensure_checkpoint(
        name=name,
        vertical_id=vertical_id,
        source=source,
        start_day=start_day,
        end_day=end_day,
    )

    if seed_last_completed_day and start_day <= seed_last_completed_day <= end_day:
        seed_checkpoint(
            name=name,
            vertical_id=vertical_id,
            source=source,
            seed_last_completed_day=seed_last_completed_day,
        )
        state = get_checkpoint(name=name, vertical_id=vertical_id, source=source) or state

    cur = next_day_to_run(state)
    if cur > end_day:
        mark_checkpoint_complete(name=name, vertical_id=vertical_id, source=source)
        log.info("backfill_window_complete name=%s vertical_id=%s", name, vertical_id)
        return

    total_days = (end_day - start_day).days + 1
    done_days = 0
    if state.last_completed_day:
        done_days = max(0, (state.last_completed_day - start_day).days + 1)

    _emit_metric("backfill_days_total", total_days, window=name, vertical_id=vertical_id)
    _emit_metric("backfill_days_completed", done_days, window=name, vertical_id=vertical_id)

    while cur <= end_day:
        run_id = new_run_id(day=cur)
        run_day_fn(
            vertical_id=int(vertical_id),
            source=str(source),
            d=cur,
            run_id=run_id,
            query=query,
            limit=limit,
            offset=offset,
        )
        mark_checkpoint_progress(
            name=name,
            vertical_id=vertical_id,
            source=source,
            last_completed_day=cur,
        )
        _emit_metric("backfill_day_completed", 1, window=name, day=cur.isoformat(), vertical_id=vertical_id)
        cur += timedelta(days=1)

    mark_checkpoint_complete(name=name, vertical_id=vertical_id, source=source)
    _emit_metric("backfill_window_complete", 1, window=name, vertical_id=vertical_id)


def _run_backfill_series(
    *,
    vertical_id: int,
    source: str,
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    start: Optional[date],
    end: Optional[date],
) -> None:
    """
    Run the default backfill series: 7d then 90d.
    """
    _run_backfill_window(
        name="backfill_7d",
        vertical_id=vertical_id,
        source=source,
        days=7,
        start=start,
        end=end,
        query=query,
        limit=limit,
        offset=offset,
    )

    seed_state = get_checkpoint(name="backfill_7d", vertical_id=vertical_id, source=source)
    seed_last = seed_state.last_completed_day if seed_state else None

    _run_backfill_window(
        name="backfill_90d",
        vertical_id=vertical_id,
        source=source,
        days=90,
        start=start,
        end=end,
        query=query,
        limit=limit,
        offset=offset,
        seed_last_completed_day=seed_last,
    )


def main() -> None:
    args = _parse_args()

    if args.mode == "once":
        _run_once_infer_day_then_sequential(
            vertical_id=int(args.vertical_id),
            source=str(args.source),
            query=args.query,
            limit=args.limit,
            offset=args.offset,
        )
        return

    start = _parse_day(args.start)
    end = _parse_day(args.end)

    if start or end:
        args.series = False

    if args.series:
        _run_backfill_series(
            vertical_id=int(args.vertical_id),
            source=str(args.source),
            query=args.query,
            limit=args.limit,
            offset=args.offset,
            start=start,
            end=end,
        )
        return

    window_name = "backfill_custom"
    if start is None and end is None:
        window_name = f"backfill_{int(args.days)}d"

    _run_backfill_window(
        name=window_name,
        vertical_id=int(args.vertical_id),
        source=str(args.source),
        days=int(args.days),
        start=start,
        end=end,
        query=args.query,
        limit=args.limit,
        offset=args.offset,
    )


if __name__ == "__main__":
    main()
