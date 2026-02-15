from __future__ import annotations

import os
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from db.session import SessionLocal
from db.repos import verticals as vertical_repo
from scheduler import main as scheduler_main


FIXTURES_DIR = Path(os.getenv("VERTICAL_FIXTURES_DIR", "/app/tools/fixtures/verticals"))


@dataclass
class RunStatus:
    id: str
    mode: str
    status: str
    started_at: float
    finished_at: float | None
    detail: str | None


_runs: Dict[str, RunStatus] = {}
_runs_lock = threading.Lock()


def _set_status(run_id: str, **updates: Any) -> None:
    with _runs_lock:
        s = _runs.get(run_id)
        if s is None:
            return
        for k, v in updates.items():
            setattr(s, k, v)


def list_runs() -> List[Dict[str, Any]]:
    with _runs_lock:
        return [s.__dict__.copy() for s in _runs.values()]


def _parse_fixture(path: Path) -> Dict[str, Any]:
    name = None
    description = None
    queries: list[str] = []
    in_queries = False

    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.rstrip("\n")
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("name:"):
            name = s.split(":", 1)[1].strip().strip("\"").strip("'")
            in_queries = False
            continue
        if s.startswith("description:"):
            description = s.split(":", 1)[1].strip().strip("\"").strip("'")
            continue
        if s.startswith("default_queries:"):
            in_queries = True
            continue
        if in_queries:
            if s.startswith("-"):
                q = s[1:].strip().strip("\"").strip("'")
                if q:
                    queries.append(q)
                continue
            if not raw.startswith(" "):
                in_queries = False

    if not name:
        raise ValueError(f"Fixture missing name: {path}")

    return {
        "name": name,
        "description": description,
        "default_queries": queries,
        "path": str(path),
    }


def list_fixtures() -> List[Dict[str, Any]]:
    if not FIXTURES_DIR.exists():
        return []
    items: list[Dict[str, Any]] = []
    for p in sorted(FIXTURES_DIR.glob("*.yml")):
        try:
            items.append(_parse_fixture(p))
        except Exception:
            continue
    return items


def _ensure_vertical(name: str) -> int:
    db = SessionLocal()
    try:
        v = vertical_repo.get_by_name(db, name)
        if v is None:
            v = vertical_repo.create(db, name)
        return int(v.id)
    finally:
        db.close()


def _run_single(vertical_id: int, source: str, query: str | None, limit: int | None) -> None:
    scheduler_main._run_once_infer_day_then_sequential(
        vertical_id=vertical_id,
        source=source,
        query=query,
        limit=limit,
        offset=None,
    )


def _run_yaml(path: Path, source: str, limit: int | None) -> None:
    fixture = _parse_fixture(path)
    vertical_id = _ensure_vertical(fixture["name"])
    for q in fixture.get("default_queries") or []:
        _run_single(vertical_id=vertical_id, source=source, query=q, limit=limit)
        time.sleep(0.5)


def start_run(*, mode: str, vertical_id: int | None, source: str, query: str | None, limit: int | None, fixture_name: str | None) -> str:
    run_id = str(uuid.uuid4())
    status = RunStatus(
        id=run_id,
        mode=mode,
        status="running",
        started_at=time.time(),
        finished_at=None,
        detail=None,
    )
    with _runs_lock:
        _runs[run_id] = status

    def _worker():
        try:
            if mode == "single":
                if vertical_id is None:
                    raise ValueError("vertical_id is required for single mode")
                _run_single(vertical_id=vertical_id, source=source, query=query, limit=limit)
            elif mode == "yaml":
                if not fixture_name:
                    raise ValueError("fixture_name is required for yaml mode")
                if not FIXTURES_DIR.exists():
                    raise ValueError("fixtures directory not available")
                path = FIXTURES_DIR / fixture_name
                if not path.exists():
                    raise ValueError(f"fixture not found: {fixture_name}")
                _run_yaml(path=path, source=source, limit=limit)
            else:
                raise ValueError(f"Unknown mode: {mode}")
            _set_status(run_id, status="success", finished_at=time.time())
        except Exception as exc:
            _set_status(run_id, status="error", finished_at=time.time(), detail=str(exc))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

    return run_id
