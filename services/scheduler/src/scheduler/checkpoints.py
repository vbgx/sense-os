from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models import SchedulerCheckpoint
from db.session import SessionLocal

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class CheckpointState:
    """
    Snapshot of a scheduler checkpoint.
    """

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


def get_checkpoint(
    *,
    name: str,
    vertical_id: int,
    source: str,
    db: Session | None = None,
) -> CheckpointState | None:
    """
    Fetch a checkpoint state for a given (name, vertical_id, source).
    """
    owns_db = db is None
    db = db or SessionLocal()
    try:
        row = (
            db.query(SchedulerCheckpoint)
            .filter(SchedulerCheckpoint.name == str(name))
            .filter(SchedulerCheckpoint.vertical_id == int(vertical_id))
            .filter(SchedulerCheckpoint.source == str(source))
            .one_or_none()
        )
        return _as_state(row) if row else None
    finally:
        if owns_db:
            db.close()


def ensure_checkpoint(
    *,
    name: str,
    vertical_id: int,
    source: str,
    start_day: date,
    end_day: date,
    db: Session | None = None,
) -> CheckpointState:
    """
    Create or update a checkpoint for a backfill window.
    """
    owns_db = db is None
    db = db or SessionLocal()
    try:
        row = (
            db.query(SchedulerCheckpoint)
            .filter(SchedulerCheckpoint.name == str(name))
            .filter(SchedulerCheckpoint.vertical_id == int(vertical_id))
            .filter(SchedulerCheckpoint.source == str(source))
            .one_or_none()
        )

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
            return _as_state(row)

        if row.start_day != start_day or row.end_day != end_day:
            row.start_day = start_day
            row.end_day = end_day
            if row.last_completed_day:
                if row.last_completed_day < start_day or row.last_completed_day > end_day:
                    row.last_completed_day = None
            row.status = "running"
            row.updated_at = func.now()
            db.add(row)
            db.commit()
            db.refresh(row)

        return _as_state(row)
    finally:
        if owns_db:
            db.close()


def seed_checkpoint(
    *,
    name: str,
    vertical_id: int,
    source: str,
    seed_last_completed_day: date,
    db: Session | None = None,
) -> CheckpointState | None:
    """
    Seed a checkpoint's last_completed_day if it is empty.
    """
    owns_db = db is None
    db = db or SessionLocal()
    try:
        row = (
            db.query(SchedulerCheckpoint)
            .filter(SchedulerCheckpoint.name == str(name))
            .filter(SchedulerCheckpoint.vertical_id == int(vertical_id))
            .filter(SchedulerCheckpoint.source == str(source))
            .one_or_none()
        )
        if row is None:
            return None
        if row.last_completed_day is None:
            row.last_completed_day = seed_last_completed_day
            row.status = "running"
            row.updated_at = func.now()
            db.add(row)
            db.commit()
            db.refresh(row)
        return _as_state(row)
    finally:
        if owns_db:
            db.close()


def mark_checkpoint_progress(
    *,
    name: str,
    vertical_id: int,
    source: str,
    last_completed_day: date,
    db: Session | None = None,
) -> CheckpointState:
    """
    Update checkpoint progress after completing a day.
    """
    owns_db = db is None
    db = db or SessionLocal()
    try:
        row = (
            db.query(SchedulerCheckpoint)
            .filter(SchedulerCheckpoint.name == str(name))
            .filter(SchedulerCheckpoint.vertical_id == int(vertical_id))
            .filter(SchedulerCheckpoint.source == str(source))
            .one()
        )
        row.last_completed_day = last_completed_day
        row.status = "running"
        row.updated_at = func.now()
        db.add(row)
        db.commit()
        db.refresh(row)
        return _as_state(row)
    finally:
        if owns_db:
            db.close()


def mark_checkpoint_complete(
    *,
    name: str,
    vertical_id: int,
    source: str,
    db: Session | None = None,
) -> CheckpointState:
    """
    Mark a checkpoint as complete.
    """
    owns_db = db is None
    db = db or SessionLocal()
    try:
        row = (
            db.query(SchedulerCheckpoint)
            .filter(SchedulerCheckpoint.name == str(name))
            .filter(SchedulerCheckpoint.vertical_id == int(vertical_id))
            .filter(SchedulerCheckpoint.source == str(source))
            .one()
        )
        row.status = "complete"
        row.updated_at = func.now()
        db.add(row)
        db.commit()
        db.refresh(row)
        return _as_state(row)
    finally:
        if owns_db:
            db.close()


def next_day_to_run(state: CheckpointState) -> date:
    """
    Return the next day to process based on last_completed_day.
    """
    if state.last_completed_day is None:
        return state.start_day
    return state.last_completed_day + timedelta(days=1)
