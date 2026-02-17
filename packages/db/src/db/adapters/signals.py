from __future__ import annotations

from typing import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from db import models
from db.repos import signals as signals_repo


class SignalsAdapter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_vertical(self, *, vertical_id: int, limit: int, offset: int):
        return signals_repo.list_by_vertical(
            self._session,
            vertical_id=int(vertical_id),
            limit=int(limit),
            offset=int(offset),
        )

    def count_by_vertical(self, *, vertical_id: int) -> int:
        return int(
            self._session.query(func.count(models.Signal.id))
            .filter(models.Signal.vertical_id == int(vertical_id))
            .scalar()
            or 0
        )

    def get_by_ids(self, ids: Sequence[int]):
        if not ids:
            return []
        return (
            self._session.query(models.Signal)
            .filter(models.Signal.id.in_([int(x) for x in ids]))
            .all()
        )
