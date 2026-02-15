from sqlalchemy.orm import Session
from ..models import Vertical


def get_all(db: Session):
    return db.query(Vertical).all()


def get_by_name(db: Session, name: str):
    return db.query(Vertical).filter(Vertical.name == name).one_or_none()


def create(db: Session, name: str):
    vertical = Vertical(name=name)
    db.add(vertical)
    db.commit()
    db.refresh(vertical)
    return vertical
