from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db import models


def create_if_absent(
    db: Session,
    *,
    vertical_db_id: int | None = None,
    vertical_id: str | None = None,
    taxonomy_version: str | None = None,
    source: str,
    external_id: str,
    content: str,
    url: str | None,
    created_at: Optional[datetime] = None,
) -> Tuple[models.Signal, bool]:
    if db.bind and db.bind.dialect.name == "postgresql":
        values = {
            "source": str(source),
            "external_id": str(external_id),
            "content": str(content),
            "url": url,
            "created_at": created_at,
        }
        if vertical_db_id is not None:
            values["vertical_db_id"] = int(vertical_db_id)
        if vertical_id is not None:
            values["vertical_id"] = str(vertical_id)
        if taxonomy_version is not None:
            values["taxonomy_version"] = str(taxonomy_version)
        stmt = (
            pg_insert(models.Signal)
            .values(**values)
            .on_conflict_do_nothing(index_elements=["source", "external_id"])
            .returning(models.Signal.id)
        )
        inserted_id = db.execute(stmt).scalar_one_or_none()
        if inserted_id is not None:
            row = db.get(models.Signal, inserted_id)
            if row is not None:
                return row, True

        existing = (
            db.query(models.Signal)
            .filter(models.Signal.source == str(source))
            .filter(models.Signal.external_id == str(external_id))
            .one_or_none()
        )
        if existing is None:
            raise RuntimeError("signal insert conflict but row missing")
        return existing, False

    existing = (
        db.query(models.Signal)
        .filter(models.Signal.source == str(source))
        .filter(models.Signal.external_id == str(external_id))
        .one_or_none()
    )
    if existing is not None:
        return existing, False

    row_kwargs = {
        "source": str(source),
        "external_id": str(external_id),
        "content": str(content),
        "url": url,
        "created_at": created_at,
    }
    if vertical_db_id is not None:
        row_kwargs["vertical_db_id"] = int(vertical_db_id)
    if vertical_id is not None:
        row_kwargs["vertical_id"] = str(vertical_id)
    if taxonomy_version is not None:
        row_kwargs["taxonomy_version"] = str(taxonomy_version)
    row = models.Signal(**row_kwargs)
    db.add(row)
    db.flush()
    return row, True


def list_by_vertical_db_id(
    db: Session,
    *,
    vertical_db_id: int,
    limit: int,
    offset: int,
    language_codes: Optional[Sequence[str]] = None,
) -> List[models.Signal]:
    q = (
        db.query(models.Signal)
        .filter(models.Signal.vertical_db_id == int(vertical_db_id))
        .order_by(models.Signal.id.asc())
    )
    if language_codes:
        q = q.filter(models.Signal.language_code.in_([str(x) for x in language_codes]))
    return q.limit(int(limit)).offset(int(offset)).all()


def set_signal_quality_score(
    db: Session,
    *,
    signal_id: int,
    signal_quality_score: int,
) -> None:
    db.query(models.Signal).filter(models.Signal.id == int(signal_id)).update(
        {"signal_quality_score": int(signal_quality_score)}
    )


def set_language_code(
    db: Session,
    *,
    signal_id: int,
    language_code: str,
) -> None:
    db.query(models.Signal).filter(models.Signal.id == int(signal_id)).update(
        {"language_code": str(language_code)}
    )


def set_spam_score(
    db: Session,
    *,
    signal_id: int,
    spam_score: int,
) -> None:
    db.query(models.Signal).filter(models.Signal.id == int(signal_id)).update(
        {"spam_score": int(spam_score)}
    )
