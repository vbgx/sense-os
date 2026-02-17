from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import os
import json
import yaml
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/verticals", tags=["verticals"])

VERTICALS_DIR = Path(os.getenv("VERTICALS_DIR", "/app/config/verticals"))

INDEX_FILE_JSON = VERTICALS_DIR / "verticals.json"
def _read_doc(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8")) or {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_index() -> Optional[List[Dict[str, Any]]]:
    if not INDEX_FILE_JSON.exists():
        return None
    data = _read_doc(INDEX_FILE_JSON)
    items = data.get("verticals")
    if not isinstance(items, list):
        return None
    if not items or not all(isinstance(x, dict) for x in items):
        return None
    if not any("file" in x for x in items):
        return None
    return items


def _discover_vertical_files() -> List[Path]:
    # Legacy fallback: all yml/json except the index file itself
    if not VERTICALS_DIR.exists():
        return []
    files = []
    for ext in ("*.json", "*.yml"):
        files.extend(VERTICALS_DIR.glob(ext))
    files = [p for p in files if p.name not in ("verticals.json")]
    return sorted(files, key=lambda p: p.name)


def _load_vertical_by_file(path: Path) -> Dict[str, Any]:
    data = _read_doc(path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid vertical doc (expected mapping): {path}")
    vid = data.get("id") or data.get("name") or path.stem
    data.setdefault("id", vid)
    data.setdefault("name", vid)
    return data


def _load_all_verticals() -> List[Dict[str, Any]]:
    idx = _load_index()
    out: List[Dict[str, Any]] = []

    if idx is not None:
        for entry in idx:
            enabled = entry.get("enabled", True)
            if enabled is False:
                continue

            file_name = entry.get("file")
            if not file_name:
                continue

            p = (VERTICALS_DIR / str(file_name)).resolve()
            if not p.exists():
                raise HTTPException(status_code=500, detail=f"Vertical file missing: {file_name}")

            v = _load_vertical_by_file(p)

            v["_index"] = {
                "priority": entry.get("priority", 1000),
                "file": file_name,
            }

            if entry.get("id"):
                v["id"] = entry["id"]
                v.setdefault("name", entry["id"])

            out.append(v)

        out.sort(key=lambda x: int((x.get("_index") or {}).get("priority", 1000)))
        return out

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
