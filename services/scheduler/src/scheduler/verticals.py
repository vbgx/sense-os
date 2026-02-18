from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from db.init_db import init_db
from db.session import SessionLocal
from db.repos import verticals as vertical_repo


@dataclass(frozen=True, slots=True)
class VerticalSpec:
    id: str
    enabled: bool
    priority: int
    path: str
    title: str | None = None
    default_queries: list[str] | None = None

    # Optional per-vertical ingestion sources (from JSON)
    # If None/empty => scheduler will fallback to "all available adapters"
    ingestion_sources: list[str] | None = None


def ensure_vertical(name: str) -> int:
    init_db()
    db = SessionLocal()
    try:
        v = vertical_repo.get_by_name(db, name)
        if v is None:
            v = vertical_repo.create(db, name=name)
        return int(v.id)
    finally:
        db.close()


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _canon(s: object) -> str:
    return str(s or "").strip()


def _dedup_str_list(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        s = _canon(x)
        if not s:
            continue
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


def _parse_default_queries(data: dict) -> list[str] | None:
    dq_raw = data.get("default_queries")
    if not isinstance(dq_raw, list):
        return None
    tmp: list[str] = []
    for x in dq_raw:
        s = _canon(x)
        if s:
            tmp.append(s)
    return _dedup_str_list(tmp) or None


def _parse_ingestion_sources(data: dict) -> list[str] | None:
    """
    Expected shapes we support:

    A) {"ingestion": {"sources": [{"name":"reddit","limit":80}, ...]}}
    B) {"sources": ["reddit","hackernews", ...]}  (fallback / legacy-friendly)
    """
    ing = data.get("ingestion")
    if isinstance(ing, dict):
        srcs = ing.get("sources")
        if isinstance(srcs, list):
            names: list[str] = []
            for it in srcs:
                if isinstance(it, dict):
                    n = _canon(it.get("name"))
                    if n:
                        names.append(n)
                elif isinstance(it, str):
                    n = _canon(it)
                    if n:
                        names.append(n)
            names = _dedup_str_list(names)
            return names or None

    # fallback: allow top-level "sources": [...]
    top = data.get("sources")
    if isinstance(top, list):
        names = _dedup_str_list([_canon(x) for x in top])
        return names or None

    return None


def scan_verticals_dir(dir_path: str | Path) -> list[VerticalSpec]:
    p = Path(dir_path)
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"verticals dir not found: {p}")

    out: list[VerticalSpec] = []
    for fp in sorted(p.glob("*.json")):
        data = _read_json(fp)
        vid = _canon(data.get("id"))
        if not vid:
            continue

        enabled = bool(data.get("enabled", True))

        pr = data.get("priority")
        try:
            priority = int(pr) if pr is not None else 10_000
        except Exception:
            priority = 10_000

        title = data.get("title")
        title_s = _canon(title) if title is not None else None

        default_queries = _parse_default_queries(data)
        ingestion_sources = _parse_ingestion_sources(data)

        out.append(
            VerticalSpec(
                id=vid,
                enabled=enabled,
                priority=priority,
                path=str(fp),
                title=title_s or None,
                default_queries=default_queries,
                ingestion_sources=ingestion_sources,
            )
        )

    out.sort(key=lambda v: (int(v.priority), v.id))
    return out


def iter_verticals(
    *,
    dir_path: str | Path,
    enabled_only: bool = True,
    only_prefix: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> Iterator[VerticalSpec]:
    vs = scan_verticals_dir(dir_path)

    if enabled_only:
        vs = [v for v in vs if v.enabled]

    if only_prefix:
        pref = str(only_prefix)
        vs = [v for v in vs if v.id.startswith(pref)]

    if offset:
        vs = vs[int(offset) :]

    if limit is not None:
        vs = vs[: int(limit)]

    yield from vs
