from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models import SchedulerCheckpoint


def get_row(
    db: Session,
    *,
    name: str,
    vertical_id: int,
    source: str,
) -> Optional[SchedulerCheckpoint]:
    return (
        db.query(SchedulerCheckpoint)
        .filter(SchedulerCheckpoint.name == str(name))
        .filter(SchedulerCheckpoint.vertical_id == int(vertical_id))
        .filter(SchedulerCheckpoint.source == str(source))
        .one_or_none()
    )


def touch(
    db: Session,
    *,
    name: str,
    vertical_id: int,
    source: str,
    start_day: date,
    end_day: date,
) -> SchedulerCheckpoint:
    """
    Create if missing, otherwise update updated_at and (optionally) window.
    """
    row = get_row(db, name=name, vertical_id=vertical_id, source=source)
    if row is None:
        row = SchedulerCheckpoint(
            name=str(name),
            vertical_id=int(vertical_id),
            source=str(source),
            start_day=start_day,
            end_day=end_day,
            last_completed_day=None,
            status="running",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    # Keep window consistent
    if row.start_day != start_day or row.end_day != end_day:
        row.start_day = start_day
        row.end_day = end_day
        if row.last_completed_day and (row.last_completed_day < start_day or row.last_completed_day > end_day):
            row.last_completed_day = None

    row.status = "running"
    row.updated_at = func.now()
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
