from __future__ import annotations

from dataclasses import dataclass

from application.ports import UnitOfWork


@dataclass
class SignalsUseCase:
    uow: UnitOfWork

    def list_signals(self, *, vertical_id: int, limit: int, offset: int):
        with self.uow:
            rows = self.uow.signals.list_by_vertical(
                vertical_id=int(vertical_id),
                limit=int(limit),
                offset=int(offset),
            )
            total = self.uow.signals.count_by_vertical(vertical_id=int(vertical_id))
        return rows, int(total)
