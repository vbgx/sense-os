from __future__ import annotations

from dataclasses import dataclass

from application.ports import UnitOfWork


@dataclass
class VerticalsUseCase:
    uow: UnitOfWork

    def list_verticals(self):
        with self.uow:
            return self.uow.verticals.get_all()

    def create_vertical(self, *, name: str):
        with self.uow:
            return self.uow.verticals.create(name=name)

    def ensure_vertical(self, *, name: str) -> int:
        with self.uow:
            v = self.uow.verticals.get_by_name(name)
            if v is None:
                v = self.uow.verticals.create(name=name)
        return int(getattr(v, "id"))
