from __future__ import annotations

from fastapi import APIRouter, Depends
from api_gateway.dependencies import get_meta_use_case
from api_gateway.schemas.meta import MetaStatusOut
from application.use_cases.meta import MetaUseCase

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/status", response_model=MetaStatusOut)
def get_meta_status(use_case: MetaUseCase = Depends(get_meta_use_case)):
    return use_case.get_status()
