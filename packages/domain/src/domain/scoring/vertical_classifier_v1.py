from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class VerticalDoc:
    id: str
    data: Dict[str, Any]


def _read_doc(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix != ".json":
        raise ValueError(f"YAML is not supported (JSON-only): {path}")
    d = json.loads(path.read_text(encoding="utf-8")) or {}
    if not isinstance(d, dict):
        raise ValueError(f"Invalid vertical JSON (expected object): {path}")
    return d


def _list_vertical_files(base_dir: Path) -> List[Path]:
    # JSON-only: prefer *.json if any exist
    json_files = sorted(base_dir.glob("*.json"))
    json_files = [p for p in json_files if p.name != "verticals.json"]
    return json_files


def _load_verticals(base_dir: Path) -> List[VerticalDoc]:
    out: List[VerticalDoc] = []
    for p in _list_vertical_files(base_dir):
        d = _read_doc(p)
        vid = str(d.get("id") or d.get("name") or p.stem)
        d.setdefault("id", vid)
        d.setdefault("name", vid)
        out.append(VerticalDoc(id=vid, data=d))
    return out


def _default_verticals_dir() -> Path:
    # matches API default
    return Path(os.environ.get("VERTICALS_DIR", "config/verticals"))


def load_vertical_docs(verticals_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    base = verticals_dir or _default_verticals_dir()
    if not base.exists():
        raise RuntimeError(
            "Vertical fixtures not found. Set VERTICALS_DIR or ensure config/verticals is available."
        )
    return [v.data for v in _load_verticals(base)]
