from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models import SchedulerCheckpoint
from db.session import SessionLocal


CHECKPOINT_NAME = "ingestion_fetch"


@dataclass(frozen=True)
class CheckpointState:
    name: str
    vertical_id: int
    source: str
    start_day: date
    end_day: date
    last_completed_day: Optional[date]
    status: str


def _as_state(cp: SchedulerCheckpoint) -> CheckpointState:
    return CheckpointState(
        name=str(cp.name),
        vertical_id=int(cp.vertical_id),
        source=str(cp.source),
        start_day=cp.start_day,
        end_day=cp.end_day,
        last_completed_day=cp.last_completed_day,
        status=str(cp.status),
    )


def _ensure(
    *,
    vertical_db_id: int,
    source: str,
    start_day: date,
    end_day: date,
    db: Session,
) -> CheckpointState:
    row = (
        db.query(SchedulerCheckpoint)
        .filter(SchedulerCheckpoint.name == CHECKPOINT_NAME)
        .filter(SchedulerCheckpoint.vertical_id == int(vertical_db_id))
        .filter(SchedulerCheckpoint.source == str(source))
        .one_or_none()
    )

    if row is None:
        row = SchedulerCheckpoint(
            name=CHECKPOINT_NAME,
            vertical_id=int(vertical_db_id),
            source=str(source),
            start_day=start_day,
            end_day=end_day,
            last_completed_day=None,
            status="running",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _as_state(row)

    if row.start_day != start_day or row.end_day != end_day:
        row.start_day = start_day
        row.end_day = end_day
        if row.last_completed_day is not None:
            if row.last_completed_day < start_day or row.last_completed_day > end_day:
                row.last_completed_day = None
        row.status = "running"
        row.updated_at = func.now()
        db.add(row)
        db.commit()
        db.refresh(row)

    return _as_state(row)


def should_skip_fetch(
    *,
    vertical_db_id: int,
    source: str,
    start_day: date,
    end_day: date,
) -> bool:
    db = SessionLocal()
    try:
        st = _ensure(
            vertical_db_id=int(vertical_db_id),
            source=str(source),
            start_day=start_day,
            end_day=end_day,
            db=db,
        )
        if st.last_completed_day is None:
            return False
        return st.last_completed_day >= end_day
    finally:
        db.close()


def mark_fetched(
    *,
    vertical_db_id: int,
    source: str,
    start_day: date,
    end_day: date,
) -> None:
    db = SessionLocal()
    try:
        _ensure(
            vertical_db_id=int(vertical_db_id),
            source=str(source),
            start_day=start_day,
            end_day=end_day,
            db=db,
        )
        row = (
            db.query(SchedulerCheckpoint)
            .filter(SchedulerCheckpoint.name == CHECKPOINT_NAME)
            .filter(SchedulerCheckpoint.vertical_id == int(vertical_db_id))
            .filter(SchedulerCheckpoint.source == str(source))
            .one()
        )
        row.last_completed_day = end_day
        row.status = "complete" if end_day >= row.end_day else "running"
        row.updated_at = func.now()
        db.add(row)
        db.commit()
    finally:
        db.close()
