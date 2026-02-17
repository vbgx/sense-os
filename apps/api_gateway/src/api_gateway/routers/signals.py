from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api_gateway.dependencies import get_signals_use_case
from api_gateway.schemas.signals import SignalListOut
from application.use_cases.signals import SignalsUseCase

router = APIRouter(tags=["signals"])


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _dt(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, datetime):
        return v.isoformat()
    try:
        return str(v)
    except Exception:
        return None


@router.get("/signals", response_model=SignalListOut)
def signals_list(
    *,
    use_case: SignalsUseCase = Depends(get_signals_use_case),
    vertical_id: Optional[int] = Query(default=None, ge=1),
    vertical: Optional[int] = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    vid = vertical_id if vertical_id is not None else vertical
    if vid is None:
        raise HTTPException(status_code=422, detail="vertical_id is required (e.g. ?vertical_id=1)")

    rows, total = use_case.list_signals(vertical_id=int(vid), limit=limit, offset=offset)
    items = [
        {
            "id": int(_get(s, "id")),
            "vertical_id": int(_get(s, "vertical_id")),
            "source": str(_get(s, "source")),
            "external_id": str(_get(s, "external_id")),
            "content": str(_get(s, "content")),
            "url": _get(s, "url"),
            "created_at": _dt(_get(s, "created_at")),
            "ingested_at": _dt(_get(s, "ingested_at")),
        }
        for s in (rows or [])
    ]

    return {
        "items": items,
        "total": int(total or 0),
        "page": {"limit": int(limit), "offset": int(offset)},
    }
