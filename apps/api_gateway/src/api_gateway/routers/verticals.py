from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException

from api_gateway.dependencies import get_verticals_use_case
from api_gateway.schemas.export_payload import VentureOSExportPayloadV1Schema
from api_gateway.schemas.verticals import VerticalListOut
from application.ports import NotFoundError
from application.use_cases.verticals import VerticalsUseCase

router = APIRouter(prefix="/verticals", tags=["verticals"])

_DEFAULT_VERTICALS_DIR = Path(os.getenv("VERTICALS_DIR", "/app/config/verticals"))
if _DEFAULT_VERTICALS_DIR.exists():
    VERTICALS_DIR = _DEFAULT_VERTICALS_DIR
else:
    repo_root = Path(__file__).resolve().parents[5]
    fallback = repo_root / "config" / "verticals"
    VERTICALS_DIR = fallback if fallback.exists() else _DEFAULT_VERTICALS_DIR
INDEX_FILE_JSON = VERTICALS_DIR / "verticals.json"
INDEX_FILE_YML = VERTICALS_DIR / "verticals.yml"  # legacy-only (not used if JSON exists)


def _read_doc(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8")) or {}
    # JSON-only mode: refuse YAML
    raise ValueError(f"YAML is not supported (JSON-only): {path}")


def _load_index() -> Optional[Tuple[List[Dict[str, Any]], str]]:
    """
    Index v1 (JSON):
      {
        "taxonomy_version": "YYYY-MM-DD",
        "verticals": [
          { "id": "...", "file": "...", "enabled": true, "priority": 10, "meta": {...}, "tier": "core" },
          ...
        ]
      }
    """
    if INDEX_FILE_JSON.exists():
        data = _read_doc(INDEX_FILE_JSON)
        items = data.get("verticals")
        if isinstance(items, list) and items and all(isinstance(x, dict) for x in items):
            taxonomy_version = str(data.get("taxonomy_version") or "").strip() or "unknown"
            return items, taxonomy_version
        return None

    # legacy fallback: allow old YAML index only if someone kept it (but JSON-only will refuse reading it)
    if INDEX_FILE_YML.exists():
        return None

    return None


def _discover_vertical_files() -> List[Path]:
    # JSON-only discovery: all *.json except the index
    if not VERTICALS_DIR.exists():
        return []
    files = sorted([p for p in VERTICALS_DIR.glob("*.json") if p.name != "verticals.json"])
    return files


def _load_vertical_by_file(path: Path) -> Dict[str, Any]:
    data = _read_doc(path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid vertical JSON (expected object): {path}")
    vid = data.get("id") or data.get("name") or path.stem
    data.setdefault("id", vid)
    data.setdefault("name", vid)
    return data


def _load_all_verticals() -> List[Dict[str, Any]]:
    idx = _load_index()
    out: List[Dict[str, Any]] = []
    taxonomy_version = "unknown"

    if idx is not None:
        index_items, taxonomy_version = idx
        for entry in index_items:
            if entry.get("enabled", True) is False:
                continue

            file_name = entry.get("file")
            if not file_name:
                continue

            p = (VERTICALS_DIR / str(file_name)).resolve()
            if not p.exists():
                raise HTTPException(status_code=500, detail=f"Vertical file missing: {file_name}")

            v = _load_vertical_by_file(p)
            v["_index"] = {"priority": entry.get("priority", 1000), "file": file_name}

            if entry.get("id"):
                v["id"] = entry["id"]
                v.setdefault("name", entry["id"])

            if entry.get("meta") is not None and not v.get("meta"):
                v["meta"] = entry["meta"]

            if entry.get("tier") is not None and not v.get("tier"):
                v["tier"] = entry["tier"]

            entry_taxonomy = entry.get("taxonomy_version") or taxonomy_version
            if entry_taxonomy and not v.get("taxonomy_version"):
                v["taxonomy_version"] = entry_taxonomy

            out.append(v)

        out.sort(key=lambda x: int((x.get("_index") or {}).get("priority", 1000)))
        return out

    # No index: list *.json
    for p in _discover_vertical_files():
        v = _load_vertical_by_file(p)
        v.setdefault("taxonomy_version", taxonomy_version)
        out.append(v)
    out.sort(key=lambda x: str(x.get("id", "")))
    return out


@router.get("/", response_model=VerticalListOut)
def list_verticals() -> Dict[str, Any]:
    verticals = _load_all_verticals()

    items = []
    for v in verticals:
        items.append(
            {
                "id": v.get("id"),
                "name": v.get("name"),
                "title": v.get("title"),
                "description": v.get("description"),
                "enabled": v.get("enabled", True),
                "tags": v.get("tags", []),
                "meta": v.get("meta"),
                "tier": v.get("tier"),
                "taxonomy_version": v.get("taxonomy_version"),
            }
        )
    return {"items": items}


@router.get("/{vertical_id}")
def get_vertical(vertical_id: str) -> Dict[str, Any]:
    verticals = _load_all_verticals()
    for v in verticals:
        if str(v.get("id")) == vertical_id or str(v.get("name")) == vertical_id:
            v.pop("_index", None)
            return v
    raise HTTPException(status_code=404, detail="Vertical not found")


@router.get("/{vertical_id}/ventureos_export", response_model=VentureOSExportPayloadV1Schema)
def export_ventureos_payload(
    vertical_id: str,
    taxonomy_version: str | None = None,
    use_case: VerticalsUseCase = Depends(get_verticals_use_case),
):
    try:
        return use_case.build_ventureos_export(
            vertical_id=vertical_id,
            taxonomy_version=taxonomy_version,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
