from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from application.use_cases.verticals import VerticalsUseCase
from api_gateway.dependencies import get_verticals_use_case
from api_gateway.schemas.verticals import VerticalOut

router = APIRouter(prefix="/verticals", tags=["verticals"])


def _project_root() -> Path:
    # apps/api_gateway/src/api_gateway/routers/verticals.py -> repo root = parents[5]
    return Path(__file__).resolve().parents[5]


def _load_verticals_fixtures() -> list[VerticalOut]:
    """
    Offline/dev fallback when the DB is unavailable.

    Supported sources:
    - config/verticals/*.yml  (one file per vertical)
    - config/verticals/verticals.yml   (list or mapping)
    """
    root = _project_root()
    dir_path = root / "tools" / "fixtures" / "verticals"
    file_path = root / "tools" / "fixtures" / "verticals.yml"

    try:
        import yaml  # type: ignore
    except Exception as e:  # pragma: no cover
        # No YAML parser installed: return empty but explicit.
        raise RuntimeError("PyYAML is required for verticals fixtures fallback") from e

    vertical_names: list[str] = []

    if dir_path.exists() and dir_path.is_dir():
        for p in sorted(dir_path.glob("*.yml")):
            data: Any = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "name" in data:
                vertical_names.append(str(data["name"]))
            elif isinstance(data, str):
                vertical_names.append(data)
            else:
                # best-effort: use filename stem
                vertical_names.append(p.stem)

    if not vertical_names and file_path.exists():
        data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "name" in item:
                    vertical_names.append(str(item["name"]))
                elif isinstance(item, str):
                    vertical_names.append(item)
        elif isinstance(data, dict):
            # allow either {"verticals":[...]} or {"foo": {...}, ...}
            if "verticals" in data and isinstance(data["verticals"], list):
                for item in data["verticals"]:
                    if isinstance(item, dict) and "name" in item:
                        vertical_names.append(str(item["name"]))
                    elif isinstance(item, str):
                        vertical_names.append(item)
            else:
                for k, v in data.items():
                    if isinstance(v, dict) and "name" in v:
                        vertical_names.append(str(v["name"]))
                    else:
                        vertical_names.append(str(k))

    # De-dup while preserving order
    seen: set[str] = set()
    cleaned: list[str] = []
    for name in vertical_names:
        n = name.strip()
        if not n or n in seen:
            continue
        seen.add(n)
        cleaned.append(n)

    return [VerticalOut(id=i + 1, name=name) for i, name in enumerate(cleaned)]


@router.get("/", response_model=list[VerticalOut])
def list_verticals(use_case: VerticalsUseCase = Depends(get_verticals_use_case)):
    try:
        return use_case.list_verticals()
    except Exception:
        # DB down / not configured: serve fixtures so the UX can render.
        return _load_verticals_fixtures()


@router.post("/")
def create_vertical(name: str, use_case: VerticalsUseCase = Depends(get_verticals_use_case)):
    return use_case.create_vertical(name=name)
