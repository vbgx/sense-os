from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_gateway.dependencies import get_db
from api_gateway.services.pains_service import get_pain, list_pains

router = APIRouter()


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """
    Supports both ORM objects (attrs) and dict rows.
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _dt(v: Any) -> Optional[str]:
    """
    Convert datetime-like values to ISO strings (or passthrough str).
    """
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


def _split_row(row: Any) -> Tuple[Any, Any]:
    """
    Normalizes repo outputs into (pain, signal).

    Accepted inputs:
    - (PainInstance, Signal) tuple
    - {"pain": {...}, "signal": {...}} dict
    - {"id":..., "vertical_id":..., ...} dict (pain only)
    - {"pain_instance": {...}, "signal": {...}} dict (alt key)
    - Any ORM pain instance (no signal)
    """
    if row is None:
        return None, None

    # tuple/list from SQLAlchemy: (PainInstance, Signal)
    if isinstance(row, (tuple, list)):
        if len(row) >= 2:
            return row[0], row[1]
        if len(row) == 1:
            return row[0], None
        return None, None

    # dict shapes
    if isinstance(row, dict):
        if "pain" in row or "signal" in row:
            return row.get("pain"), row.get("signal")
        if "pain_instance" in row or "signal" in row:
            return row.get("pain_instance"), row.get("signal")
        # flat pain dict
        return row, None

    # ORM pain object
    return row, None


def _row_to_item(row: Any) -> dict:
    """
    Convert a repo row to the API response shape.
    """
    pain, signal = _split_row(row)
    if pain is None:
        raise ValueError("empty row")

    item: dict[str, Any] = {
        "id": int(_get(pain, "id")),
        "vertical_id": int(_get(pain, "vertical_id")),
        "algo_version": str(_get(pain, "algo_version")),
        "pain_score": float(_get(pain, "pain_score")),
        "breakdown": _get(pain, "breakdown", {}) or {},
        "created_at": _dt(_get(pain, "created_at")),
    }

    # optional signal projection
    if signal is not None:
        item["signal"] = {
            "id": _get(signal, "id"),
            "source": _get(signal, "source"),
            "url": _get(signal, "url"),
            "title": _get(signal, "title"),
            "ingested_at": _dt(_get(signal, "ingested_at")),
        }
    else:
        item["signal"] = None

    return item


@router.get("/pains")
def pains_list(
    *,
    db: Session = Depends(get_db),
    vertical_id: Optional[int] = Query(default=None, ge=1),
    vertical: Optional[int] = Query(default=None, ge=1),
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    List pains for a vertical with pagination.
    """
    vid = vertical_id if vertical_id is not None else vertical
    if vid is None:
        raise HTTPException(status_code=422, detail="vertical_id is required (e.g. ?vertical_id=1)")

    rows, total = list_pains(db=db, limit=limit, offset=offset, vertical_id=int(vid))
    items = [_row_to_item(r) for r in (rows or [])]

    return {
        "items": items,
        "total": int(total or 0),
        "page": {"limit": int(limit), "offset": int(offset)},
    }


@router.get("/pains/{pain_id}")
def pains_detail(*, db: Session = Depends(get_db), pain_id: int):
    """
    Fetch a single pain instance by id.
    """
    row = get_pain(db=db, pain_id=pain_id)
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return _row_to_item(row)
