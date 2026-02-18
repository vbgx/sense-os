from __future__ import annotations

from typing import Any

from sqlalchemy import text

from db.session import SessionLocal


class HdbscanParamsRepo:
    def __init__(self) -> None:
        self._Session = SessionLocal

    def get_last(self, *, vertical_db_id: int, taxonomy_version: str) -> dict[str, Any] | None:
        stmt = text(
            """
            SELECT payload
            FROM clustering_hdbscan_params
            WHERE vertical_db_id = :vertical_db_id AND taxonomy_version = :taxonomy_version
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
        with self._Session() as session:
            row = session.execute(
                stmt,
                {"vertical_db_id": vertical_db_id, "taxonomy_version": taxonomy_version},
            ).fetchone()
        return row[0] if row else None

    def insert(self, *, vertical_db_id: int, taxonomy_version: str, payload: dict[str, Any]) -> None:
        stmt = text(
            """
            INSERT INTO clustering_hdbscan_params (vertical_db_id, taxonomy_version, payload)
            VALUES (:vertical_db_id, :taxonomy_version, :payload)
            """
        )
        with self._Session() as session:
            session.execute(
                stmt,
                {"vertical_db_id": vertical_db_id, "taxonomy_version": taxonomy_version, "payload": payload},
            )
            session.commit()
