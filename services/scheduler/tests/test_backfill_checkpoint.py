from __future__ import annotations

from datetime import date

import pytest

from scheduler.checkpoints import ensure_checkpoint, get_checkpoint, mark_checkpoint_progress
from scheduler.main import _run_backfill_window


def test_backfill_window_resumes_from_checkpoint(db_session):
    """Backfill should resume from the last completed day."""
    start = date(2026, 2, 10)
    end = date(2026, 2, 12)

    ensure_checkpoint(
        name="backfill_test",
        vertical_id=1,
        source="reddit",
        start_day=start,
        end_day=end,
        db=db_session,
    )
    mark_checkpoint_progress(
        name="backfill_test",
        vertical_id=1,
        source="reddit",
        last_completed_day=start,
        db=db_session,
    )

    seen_days: list[date] = []

    def _fake_run_day(**kwargs):
        seen_days.append(kwargs["d"])

    _run_backfill_window(
        name="backfill_test",
        vertical_id="b2b_ops",
        vertical_db_id=1,
        taxonomy_version="2026-02-17",
        source="reddit",
        days=3,
        start=start,
        end=end,
        query=None,
        limit=None,
        offset=None,
        run_day_fn=_fake_run_day,
    )

    assert seen_days == [date(2026, 2, 11), date(2026, 2, 12)]

    state = get_checkpoint(name="backfill_test", vertical_id=1, source="reddit", db=db_session)
    assert state is not None
    assert state.last_completed_day == end
    assert state.status == "complete"


def test_backfill_checkpoint_survives_crash(db_session):
    """Crash during backfill should not advance the checkpoint."""
    start = date(2026, 2, 10)
    end = date(2026, 2, 10)

    ensure_checkpoint(
        name="backfill_crash",
        vertical_id=1,
        source="reddit",
        start_day=start,
        end_day=end,
        db=db_session,
    )

    def _failing_run_day(**_kwargs):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        _run_backfill_window(
            name="backfill_crash",
            vertical_id="b2b_ops",
            vertical_db_id=1,
            taxonomy_version="2026-02-17",
            source="reddit",
            days=1,
            start=start,
            end=end,
            query=None,
            limit=None,
            offset=None,
            run_day_fn=_failing_run_day,
        )

    state = get_checkpoint(name="backfill_crash", vertical_id=1, source="reddit", db=db_session)
    assert state is not None
    assert state.last_completed_day is None
