from __future__ import annotations

from dataclasses import dataclass

from application.ports import UnitOfWork


@dataclass
class SignalsUseCase:
    uow: UnitOfWork

    def list_signals(self, *, vertical_db_id: int, limit: int, offset: int):
        with self.uow:
            rows = self.uow.signals.list_by_vertical_db_id(
                vertical_db_id=int(vertical_db_id),
                limit=int(limit),
                offset=int(offset),
            )
            total = self.uow.signals.count_by_vertical_db_id(vertical_db_id=int(vertical_db_id))
        return rows, int(total)
