from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple, List, Sequence

from sqlalchemy.orm import Session

from db import models


def set_spam_score(
    db: Session,
    *,
    signal_id: int,
    spam_score: int,
) -> None:
    db.query(models.Signal).filter(models.Signal.id == int(signal_id)).update(
        {"spam_score": int(spam_score)}
    )
