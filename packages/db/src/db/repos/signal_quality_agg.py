from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from db import models


def compute_avg_quality_for_signals(db: Session, *, signal_ids: list[int]) -> float:
    if not signal_ids:
        return 0.0
    q = db.query(func.avg(models.Signal.signal_quality_score)).filter(models.Signal.id.in_(signal_ids))
    v = q.scalar()
    return float(v or 0.0)
