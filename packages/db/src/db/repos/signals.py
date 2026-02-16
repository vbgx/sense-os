from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session

from db import models


def create_if_absent(
    db: Session,
    *,
    vertical_id: int,
    source: str,
    external_id: str,
    content: str,
    url: str | None,
    created_at: Optional[datetime] = None,
) -> Tuple[models.Signal, bool]:
    q = (
        db.query(models.Signal)
        .filter(models.Signal.vertical_id == int(vertical_id))
        .filter(models.Signal.source == str(source))
        .filter(models.Signal.external_id == str(external_id))
    )
    existing = q.one_or_none()
    if existing is not None:
        return existing, False

    row = models.Signal(
        vertical_id=int(vertical_id),
        source=str(source),
        external_id=str(external_id),
        content=str(content),
        url=url,
        created_at=created_at,
    )
    db.add(row)
    db.flush()
    return row, True


def list_by_vertical(
    db: Session,
    *,
    vertical_id: int,
    limit: int,
    offset: int,
) -> List[models.Signal]:
    return (
        db.query(models.Signal)
        .filter(models.Signal.vertical_id == int(vertical_id))
        .order_by(models.Signal.id.asc())
        .limit(int(limit))
        .offset(int(offset))
        .all()
    )


def set_signal_quality_score(
    db: Session,
    *,
    signal_id: int,
    signal_quality_score: int,
) -> None:
    db.query(models.Signal).filter(models.Signal.id == int(signal_id)).update(
        {"signal_quality_score": int(signal_quality_score)}
    )
