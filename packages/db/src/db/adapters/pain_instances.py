from __future__ import annotations

from sqlalchemy.orm import Session

from db.repos import pain_instances as pain_instances_repo


class PainInstancesAdapter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_ranked(self, *, vertical_id: int, limit: int, offset: int):
        return pain_instances_repo.list_ranked(
            db=self._session,
            vertical_id=int(vertical_id),
            limit=int(limit),
            offset=int(offset),
        )

    def get_with_signal(self, *, pain_id: int):
        return pain_instances_repo.get_with_signal(db=self._session, pain_id=int(pain_id))
