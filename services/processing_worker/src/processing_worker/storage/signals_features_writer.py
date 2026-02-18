from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import text

from db.session import SessionLocal


class SignalsFeaturesWriter:
    def __init__(self) -> None:
        self._Session = SessionLocal

    def update_many(self, rows: Iterable[dict[str, Any]]) -> int:
        rows_list = list(rows)
        if not rows_list:
            return 0

        stmt = text(
            """
            UPDATE signals
            SET
              language_code = :language_code,
              spam_score = :spam_score,
              quality_score = :quality_score,
              vertical_auto_classification = :vertical_auto_classification
            WHERE id = :signal_id
            """
        )

        with self._Session() as session:
            session.execute(stmt, rows_list)
            session.commit()

        return len(rows_list)
