from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select

from db.session import SessionLocal

# NOTE:
# Align these imports/fields with your actual DB model.
# You likely already have the table in models.py. If not, add it.
from db.models import SchedulerCheckpoint  # <-- adjust if model name differs


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_checkpoint(db, *, key: str) -> Optional[SchedulerCheckpoint]:
    stmt = select(SchedulerCheckpoint).where(SchedulerCheckpoint.key == key)  # type: ignore[attr-defined]
    return db.execute(stmt).scalars().first()


def upsert_checkpoint(db, *, key: str) -> None:
    obj = get_checkpoint(db, key=key)
    if obj is None:
        obj = SchedulerCheckpoint(key=key)  # type: ignore[call-arg]
        db.add(obj)
    # common column name patterns — adapt to your migration
    if hasattr(obj, "updated_at"):
        obj.updated_at = _now()  # type: ignore[attr-defined]
    db.commit()
