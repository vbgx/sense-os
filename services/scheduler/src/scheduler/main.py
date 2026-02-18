from __future__ import annotations

import argparse
import logging
import time
from datetime import date, timedelta
from typing import Optional, Callable

from sqlalchemy import text

from db.session import SessionLocal
from db.repos import verticals as verticals_repo
from domain.versions import TAXONOMY_VERSION
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
from scheduler.verticals import ensure_vertical, iter_verticals, VerticalSpec

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("scheduler")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sense OS scheduler")

    # legacy DB-centric
    p.add_argument("--vertical-id", type=int, default=None, help="DB id (legacy)")

    # filesystem verticals
    p.add_argument("--verticals-dir", type=str, default="config/verticals")
    p.add_argument("--only-prefix", type=str, default=None)
    p.add_argument("--enabled-only", dest="enabled_only", action="store_true")
    p.add_argument("--all", dest="enabled_only", action="store_false")
    p.set_defaults(enabled_only=True)

    p.add_argument("--limit-verticals", type=int, default=None)
    p.add_argument("--offset-verticals", type=int, default=None)

    p.add_argument("--vertical", type=str, default=None, help="Vertical id (from config json id)")

    # Source is ignored, we force planner source="multi"
    p.add_argument("--source", type=str, default="multi", help="IGNORED (forced to multi). kept for compatibility")

    p.add_argument("--mode", type=str, choices=["enqueue", "once", "backfill"], default="enqueue")

    p.add_argument("--query", type=str, default=None, help="Override: use this single query for all verticals")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--offset", type=int, default=None)

    p.add_argument(
        "--max-queries-per-vertical",
        type=int,
        default=3,
        help="When query is not provided, cap default_queries used per vertical",
    )
    p.add_argument("--enqueue-full", action="store_true", help="Enqueue ingest+process+cluster+trend (default: ingest only)")
    p.add_argument("--day", type=str, default=None, help="YYYY-MM-DD day for enqueue (optional). If omitted, day=None.")

    # backfill
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--start", type=str, default=None)
    p.add_argument("--end", type=str, default=None)
    p.add_argument("--series", dest="series", action="store_true")
    p.add_argument("--no-series", dest="series", action="store_false")
    p.set_defaults(series=True)

    return p.parse_args()


def _parse_day(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def _default_day() -> date:
    return date.today() - timedelta(days=1)


def _resolve_vertical_id_from_db(vertical_db_id: int) -> str:
    db = SessionLocal()
    try:
        row = verticals_repo.get_by_id(db, int(vertical_db_id))
    finally:
        db.close()
    if row is None:
        raise SystemExit(f"vertical not found for id={vertical_db_id}")
    return str(row.name)


def _scalar(sql: str, params: Optional[dict[str, object]] = None):
    db = SessionLocal()
    try:
        return db.execute(text(sql), params or {}).scalar_one()
    finally:
        db.close()


def _scalar_int(sql: str, params: Optional[dict[str, object]] = None) -> int:
    return int(_scalar(sql, params))


def _emit_metric(name: str, value: float | int, **tags: object) -> None:
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
        if int(time.time() - t0) % 5 == 0:
            log.info("wait_progress label=%s last=%s expected>=%s", label, last, expected)
        time.sleep(1)
    raise SystemExit(
        f"timeout waiting for {label}: expected>={expected} last={last} sql={sql!r} params={params!r}"
    )


def _infer_latest_signal_day(vertical_db_id: int) -> date:
    v = _scalar(
        "select max(ingested_at)::date from signals where vertical_db_id=:vertical_db_id",
        {"vertical_db_id": vertical_db_id},
    )
    if v is None:
        raise SystemExit("could not infer day from signals (no signals ingested)")
    return v


def _run_day_sequential(
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    d: date,
    run_id: str,
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sources: list[str] | None,
) -> None:
    day_s = d.isoformat()
    day_start = d.isoformat()
    next_day = (d + timedelta(days=1)).isoformat()

    log.info("run_day vertical_id=%s vertical_db_id=%s day=%s run_id=%s", vertical_id, vertical_db_id, day_s, run_id)

    jobs = plan_vertical_run(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        source="multi",
        run_id=run_id,
        day=d,
        query=query,
        limit=limit,
        offset=offset,
        sources=sources,
    )
    ingest, process, cluster, trend = jobs

    publish_jobs([ingest])
    _wait_count_ge(
        "signals(day)",
        """
        select count(*)
        from signals
        where vertical_db_id=:vertical_db_id
          and ingested_at >= :day_start
          and ingested_at < :day_end
        """.strip(),
        {"vertical_db_id": vertical_db_id, "day_start": day_start, "day_end": next_day},
        1,
        timeout_s=90,
    )

    publish_jobs([process])
    publish_jobs([cluster])
    publish_jobs([trend])


def _run_once_infer_day_then_sequential(
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sources: list[str] | None,
) -> None:
    run_id = new_run_id()
    jobs = plan_vertical_run(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        source="multi",
        run_id=run_id,
        day=None,
        query=query,
        limit=limit,
        offset=offset,
        sources=sources,
    )
    ingest = jobs[0]
    publish_jobs([ingest])

    _wait_count_ge(
        "signals(any)",
        "select count(*) from signals where vertical_db_id=:vertical_db_id",
        {"vertical_db_id": vertical_db_id},
        1,
        timeout_s=90,
    )
    d = _infer_latest_signal_day(vertical_db_id)

    _run_day_sequential(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        d=d,
        run_id=run_id,
        query=query,
        limit=limit,
        offset=offset,
        sources=sources,
    )


def _resolve_backfill_bounds(*, days: int, start: Optional[date], end: Optional[date]) -> tuple[date, date]:
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
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    days: int,
    start: Optional[date],
    end: Optional[date],
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sources: list[str] | None,
    seed_last_completed_day: Optional[date] = None,
    run_day_fn: Callable[..., None] = _run_day_sequential,
) -> None:
    start_day, end_day = _resolve_backfill_bounds(days=days, start=start, end=end)

    state = ensure_checkpoint(
        name=name,
        vertical_id=vertical_db_id,
        source="multi",
        start_day=start_day,
        end_day=end_day,
    )

    if seed_last_completed_day and start_day <= seed_last_completed_day <= end_day:
        seed_checkpoint(
            name=name,
            vertical_id=vertical_db_id,
            source="multi",
            seed_last_completed_day=seed_last_completed_day,
        )
        state = get_checkpoint(name=name, vertical_id=vertical_db_id, source="multi") or state

    cur = next_day_to_run(state)
    if cur > end_day:
        mark_checkpoint_complete(name=name, vertical_id=vertical_db_id, source="multi")
        return

    while cur <= end_day:
        run_id = new_run_id(day=cur)
        run_day_fn(
            vertical_id=vertical_id,
            vertical_db_id=vertical_db_id,
            taxonomy_version=taxonomy_version,
            d=cur,
            run_id=run_id,
            query=query,
            limit=limit,
            offset=offset,
            sources=sources,
        )
        mark_checkpoint_progress(
            name=name,
            vertical_id=vertical_db_id,
            source="multi",
            last_completed_day=cur,
        )
        cur += timedelta(days=1)

    mark_checkpoint_complete(name=name, vertical_id=vertical_db_id, source="multi")


def _queries_for_vertical(v: VerticalSpec, *, override_query: str | None, max_q: int) -> list[str | None]:
    if override_query is not None:
        q = override_query.strip()
        return [q] if q else [None]

    qs = v.default_queries or []
    if not qs:
        return [None]

    mq = int(max_q)
    if mq <= 0:
        return [None]

    return qs[:mq]


def _enqueue_one(
    *,
    vertical_id: str,
    vertical_db_id: int,
    taxonomy_version: str,
    d: Optional[date],
    query: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    enqueue_full: bool,
    sources: list[str] | None,
) -> None:
    run_id = new_run_id(day=d) if d else new_run_id()
    jobs = plan_vertical_run(
        vertical_id=vertical_id,
        vertical_db_id=vertical_db_id,
        taxonomy_version=taxonomy_version,
        source="multi",
        run_id=run_id,
        day=d,
        query=query,
        limit=limit,
        offset=offset,
        sources=sources,
    )
    if enqueue_full:
        publish_jobs(list(jobs))
        log.info(
            "enqueued_full vertical_id=%s vertical_db_id=%s run_id=%s query=%r sources=%s",
            vertical_id,
            vertical_db_id,
            run_id,
            query,
            sources,
        )
    else:
        publish_jobs([jobs[0]])
        log.info(
            "enqueued_ingest vertical_id=%s vertical_db_id=%s run_id=%s query=%r sources=%s",
            vertical_id,
            vertical_db_id,
            run_id,
            query,
            sources,
        )


def main() -> None:
    args = _parse_args()
    taxonomy_version = TAXONOMY_VERSION
    day = _parse_day(args.day)

    selected: list[VerticalSpec] = []

    if args.vertical is not None:
        vid = str(args.vertical).strip()
        if not vid:
            raise SystemExit("--vertical is empty")
        selected = [VerticalSpec(id=vid, enabled=True, priority=0, path="", title=None, default_queries=None, ingestion_sources=None)]
    elif args.vertical_id is not None:
        vdb = int(args.vertical_id)
        vid = _resolve_vertical_id_from_db(vdb)
        selected = [VerticalSpec(id=vid, enabled=True, priority=0, path="", title=None, default_queries=None, ingestion_sources=None)]
    else:
        selected = list(
            iter_verticals(
                dir_path=args.verticals_dir,
                enabled_only=bool(args.enabled_only),
                only_prefix=args.only_prefix,
                limit=args.limit_verticals,
                offset=args.offset_verticals,
            )
        )

    if not selected:
        raise SystemExit("no verticals selected")

    log.info("selected_verticals=%s mode=%s day=%s", len(selected), args.mode, day.isoformat() if day else None)

    if args.mode == "enqueue":
        total_jobs = 0
        for v in selected:
            vdb = ensure_vertical(v.id)
            qs = _queries_for_vertical(v, override_query=args.query, max_q=int(args.max_queries_per_vertical))

            # If config defines sources, use them. Else None => planner will fallback to all adapters.
            sources = v.ingestion_sources

            for q in qs:
                _enqueue_one(
                    vertical_id=v.id,
                    vertical_db_id=vdb,
                    taxonomy_version=taxonomy_version,
                    d=day,
                    query=q,
                    limit=args.limit,
                    offset=args.offset,
                    enqueue_full=bool(args.enqueue_full),
                    sources=sources,
                )
                total_jobs += 1
        log.info("enqueue_done jobs=%s verticals=%s", total_jobs, len(selected))
        return

    # Debug modes (slow)
    for v in selected:
        vdb = ensure_vertical(v.id)
        sources = v.ingestion_sources

        if args.mode == "once":
            _run_once_infer_day_then_sequential(
                vertical_id=v.id,
                vertical_db_id=vdb,
                taxonomy_version=taxonomy_version,
                query=args.query,
                limit=args.limit,
                offset=args.offset,
                sources=sources,
            )
            continue

        start = _parse_day(args.start)
        end = _parse_day(args.end)
        if start or end:
            args.series = False

        if args.series:
            _run_backfill_window(
                name="backfill_7d",
                vertical_id=v.id,
                vertical_db_id=vdb,
                taxonomy_version=taxonomy_version,
                days=7,
                start=start,
                end=end,
                query=args.query,
                limit=args.limit,
                offset=args.offset,
                sources=sources,
            )
            seed_state = get_checkpoint(name="backfill_7d", vertical_id=vdb, source="multi")
            seed_last = seed_state.last_completed_day if seed_state else None
            _run_backfill_window(
                name="backfill_90d",
                vertical_id=v.id,
                vertical_db_id=vdb,
                taxonomy_version=taxonomy_version,
                days=90,
                start=start,
                end=end,
                query=args.query,
                limit=args.limit,
                offset=args.offset,
                sources=sources,
                seed_last_completed_day=seed_last,
            )
        else:
            window_name = "backfill_custom"
            if start is None and end is None:
                window_name = f"backfill_{int(args.days)}d"
            _run_backfill_window(
                name=window_name,
                vertical_id=v.id,
                vertical_db_id=vdb,
                taxonomy_version=taxonomy_version,
                days=int(args.days),
                start=start,
                end=end,
                query=args.query,
                limit=args.limit,
                offset=args.offset,
                sources=sources,
            )


if __name__ == "__main__":
    main()
