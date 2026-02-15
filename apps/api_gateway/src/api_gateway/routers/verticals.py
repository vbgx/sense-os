from fastapi import APIRouter
from db.session import SessionLocal
from db.repos import verticals as vertical_repo

router = APIRouter(prefix="/verticals", tags=["verticals"])


@router.post("/")
def create_vertical(name: str):
    db = SessionLocal()
    try:
        return vertical_repo.create(db, name=name)
    finally:
        db.close()
