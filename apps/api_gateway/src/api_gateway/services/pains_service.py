from __future__ import annotations

from sqlalchemy.orm import Session

from db.repos import pain_instances as pain_instances_repo


def list_pains(*, db: Session, vertical_id: int, limit: int, offset: int):
    return pain_instances_repo.list_ranked(db=db, vertical_id=vertical_id, limit=limit, offset=offset)


def get_pain(*, db: Session, pain_id: int):
    return pain_instances_repo.get_with_signal(db=db, pain_id=pain_id)
