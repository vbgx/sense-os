from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_gateway.dependencies import get_db
from api_gateway.schemas.clusters import ClusterListOut
from api_gateway.services.clusters_service import list_clusters

router = APIRouter(tags=["clusters"])


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


@router.get("/clusters", response_model=ClusterListOut)
def clusters_list(
    *,
    db: Session = Depends(get_db),
    vertical_id: Optional[int] = Query(default=None, ge=1),
    vertical: Optional[int] = Query(default=None, ge=1),
    cluster_version: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    vid = vertical_id if vertical_id is not None else vertical
    if vid is None:
        raise HTTPException(status_code=422, detail="vertical_id is required (e.g. ?vertical_id=1)")

    rows, total = list_clusters(
        db=db,
        vertical_id=int(vid),
        limit=limit,
        offset=offset,
        cluster_version=cluster_version,
    )
    items = [
        {
            "id": int(_get(c, "id")),
            "vertical_id": int(_get(c, "vertical_id")),
            "cluster_version": str(_get(c, "cluster_version")),
            "cluster_key": str(_get(c, "cluster_key")),
            "title": str(_get(c, "title")),
            "size": int(_get(c, "size")),
            "created_at": _dt(_get(c, "created_at")),
        }
        for c in (rows or [])
    ]

    return {
        "items": items,
        "total": int(total or 0),
        "page": {"limit": int(limit), "offset": int(offset)},
    }
