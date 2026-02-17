from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/verticals", tags=["verticals"])

VERTICALS_DIR = Path(os.getenv("VERTICALS_DIR", "/app/config/verticals"))
INDEX_FILE_JSON = VERTICALS_DIR / "verticals.json"
INDEX_FILE_YML = VERTICALS_DIR / "verticals.yml"  # legacy-only (not used if JSON exists)


def _read_doc(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8")) or {}
    # JSON-only mode: refuse YAML
    raise ValueError(f"YAML is not supported (JSON-only): {path}")


def _load_index() -> Optional[List[Dict[str, Any]]]:
    """
    Index v1 (JSON):
      { "verticals": [ { "id": "...", "file": "...", "enabled": true, "priority": 10 }, ... ] }
    """
    if INDEX_FILE_JSON.exists():
        data = _read_doc(INDEX_FILE_JSON)
        items = data.get("verticals")
        if isinstance(items, list) and items and all(isinstance(x, dict) for x in items):
            return items
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

    if idx is not None:
        for entry in idx:
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

            out.append(v)

        out.sort(key=lambda x: int((x.get("_index") or {}).get("priority", 1000)))
        return out

    # No index: list *.json
    for p in _discover_vertical_files():
        out.append(_load_vertical_by_file(p))
    out.sort(key=lambda x: str(x.get("id", "")))
    return out


@router.get("/")
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
