from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from ..models import Signal


def create_if_absent(db: Session, **kwargs):
    """
    Insert a Signal if it does not exist.

    Uses INSERT ... ON CONFLICT DO NOTHING to avoid per-row commits.
    Caller is responsible for committing the transaction.
    """
    stmt = (
        insert(Signal)
        .values(**kwargs)
        .on_conflict_do_nothing(index_elements=["source", "external_id"])
        .returning(Signal.id)
    )
    inserted_id = db.execute(stmt).scalar_one_or_none()
    if inserted_id is not None:
        obj = db.get(Signal, inserted_id)
        return obj, True

    existing = (
        db.query(Signal)
        .filter(Signal.source == kwargs["source"], Signal.external_id == kwargs["external_id"])
        .one()
    )
    return existing, False


def list_by_vertical(db: Session, vertical_id: int, limit: int = 200, offset: int = 0):
    return (
        db.query(Signal)
        .filter(Signal.vertical_id == vertical_id)
        .order_by(Signal.id.asc())
        .limit(limit)
        .offset(offset)
        .all()
    )
