from __future__ import annotations

from sqlalchemy.orm import Session

from db import models


def set_vertical_auto(
    db: Session,
    *,
    signal_id: int,
    vertical_auto: str,
    vertical_auto_confidence: int,
) -> None:
    db.query(models.Signal).filter(models.Signal.id == int(signal_id)).update(
        {"vertical_auto": str(vertical_auto), "vertical_auto_confidence": int(vertical_auto_confidence)}
    )
