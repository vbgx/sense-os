from __future__ import annotations

from sqlalchemy.orm import Session

from db.repos import verticals as vertical_repo


class VerticalsAdapter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self):
        return vertical_repo.get_all(self._session)

    def get_by_name(self, name: str):
        return vertical_repo.get_by_name(self._session, name)

    def create(self, name: str):
        return vertical_repo.create(self._session, name=name)
