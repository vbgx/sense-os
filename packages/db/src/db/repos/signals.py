from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation

from ..models import Signal


def create_if_absent(db: Session, **kwargs):
    signal = Signal(**kwargs)
    db.add(signal)
    try:
        db.commit()
        db.refresh(signal)
        return signal, True
    except IntegrityError as e:
        db.rollback()
        orig = getattr(e, "orig", None)
        if isinstance(orig, UniqueViolation):
            existing = (
                db.query(Signal)
                .filter(Signal.source == kwargs["source"], Signal.external_id == kwargs["external_id"])
                .one()
            )
            return existing, False
        raise


def list_by_vertical(db: Session, vertical_id: int, limit: int = 200, offset: int = 0):
    return (
        db.query(Signal)
        .filter(Signal.vertical_id == vertical_id)
        .order_by(Signal.id.asc())
        .limit(limit)
        .offset(offset)
        .all()
    )
