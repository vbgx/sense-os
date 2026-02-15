from __future__ import annotations

import argparse
import time
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import text

from db.session import SessionLocal
from scheduler.planner import plan_vertical_run
from scheduler.publisher import publish_jobs
from scheduler.run_id import new_run_id


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
    return p.parse_args()


def _parse_day(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def _default_day() -> date:
    # for backfill default window; "once" will infer day from DB after ingest
    return date.today() - timedelta(days=1)


def _scalar(sql: str):
    db = SessionLocal()
    try:
        return db.execute(text(sql)).scalar_one()
    finally:
        db.close()


def _scalar_int(sql: str) -> int:
    return int(_scalar(sql))


def _wait_count_ge(label: str, sql: str, expected: int, timeout_s: int = 90) -> int:
    t0 = time.time()
    last = 0
    while time.time() - t0 < timeout_s:
        try:
            last = _scalar_int(sql)
        except Exception:
            last = 0
        if last >= expected:
            print(f"[ok] {label}: {last}")
            return last
        # show progress occasionally so it doesn't feel "stuck"
        if int(time.time() - t0) % 5 == 0:
            print(f"[wait] {label}: last={last} expected>={expected}")
        time.sleep(1)
    raise SystemExit(f"timeout waiting for {label}: expected>={expected} last={last} sql={sql!r}")


def _infer_latest_signal_day(vertical_id: int) -> date:
    v = _scalar(f"select max(ingested_at)::date from signals where vertical_id={vertical_id}")
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
    print(f"[run] vertical_id={vertical_id} day={day_s} run_id={run_id}")

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

    publish_jobs([ingest])
    _wait_count_ge(
        "signals(day)",
        f"select count(*) from signals where vertical_id={vertical_id} and ingested_at::date='{day_s}'",
        1,
        timeout_s=90,
    )

    publish_jobs([process])
    _wait_count_ge(
        "pain_instances(day)",
        f"select count(*) from pain_instances where vertical_id={vertical_id} and created_at::date='{day_s}'",
        1,
        timeout_s=90,
    )

    publish_jobs([cluster])
    _wait_count_ge(
        "cluster_signals",
        f"""
        select count(*)
        from cluster_signals cs
        join pain_instances pi on pi.id = cs.pain_instance_id
        where pi.vertical_id={vertical_id}
        """.strip(),
        1,
        timeout_s=90,
    )

    publish_jobs([trend])
    _wait_count_ge(
        "cluster_daily_metrics(day)",
        f"select count(*) from cluster_daily_metrics where day='{day_s}'::date",
        1,
        timeout_s=90,
    )


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
    print(f"[once] publishing ingest (no assumed day) run_id={run_id} vertical_id={vertical_id} source={source}")

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
        f"select count(*) from signals where vertical_id={vertical_id}",
        1,
        timeout_s=90,
    )

    d = _infer_latest_signal_day(vertical_id)
    print(f"[once] inferred day from signals: {d.isoformat()} (run_id={run_id})")

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

    # backfill (inclusive)
    start = _parse_day(args.start)
    end = _parse_day(args.end)

    if start and end:
        if end < start:
            raise SystemExit("end must be >= start")
        day0 = start
        day1 = end
    else:
        day1 = _default_day()
        day0 = day1 - timedelta(days=int(args.days) - 1)

    cur = day0
    while cur <= day1:
        run_id = new_run_id(day=cur)
        _run_day_sequential(
            vertical_id=int(args.vertical_id),
            source=str(args.source),
            d=cur,
            run_id=run_id,
            query=args.query,
            limit=args.limit,
            offset=args.offset,
        )
        cur += timedelta(days=1)


if __name__ == "__main__":
    main()
