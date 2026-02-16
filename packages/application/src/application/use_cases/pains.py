from __future__ import annotations

from dataclasses import dataclass

from application.ports import UnitOfWork


@dataclass
class PainsUseCase:
    uow: UnitOfWork

    def list_pains(self, *, vertical_id: int, limit: int, offset: int):
        with self.uow:
            return self.uow.pain_instances.list_ranked(
                vertical_id=int(vertical_id),
                limit=int(limit),
                offset=int(offset),
            )

    def get_pain(self, *, pain_id: int):
        with self.uow:
            return self.uow.pain_instances.get_with_signal(pain_id=int(pain_id))
