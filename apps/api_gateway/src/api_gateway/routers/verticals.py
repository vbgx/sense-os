from fastapi import APIRouter, Depends
from application.use_cases.verticals import VerticalsUseCase
from api_gateway.dependencies import get_verticals_use_case
from api_gateway.schemas.verticals import VerticalOut

router = APIRouter(prefix="/verticals", tags=["verticals"])


@router.get("/", response_model=list[VerticalOut])
def list_verticals(use_case: VerticalsUseCase = Depends(get_verticals_use_case)):
    return use_case.list_verticals()


@router.post("/")
def create_vertical(name: str, use_case: VerticalsUseCase = Depends(get_verticals_use_case)):
    return use_case.create_vertical(name=name)
