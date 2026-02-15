from fastapi import APIRouter
from db.session import SessionLocal
from db.repos import verticals as vertical_repo
from api_gateway.schemas.verticals import VerticalOut

router = APIRouter(prefix="/verticals", tags=["verticals"])


@router.get("/", response_model=list[VerticalOut])
def list_verticals():
    db = SessionLocal()
    try:
        return vertical_repo.get_all(db)
    finally:
        db.close()


@router.post("/")
def create_vertical(name: str):
    db = SessionLocal()
    try:
        return vertical_repo.create(db, name=name)
    finally:
        db.close()
