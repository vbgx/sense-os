from __future__ import annotations

from dataclasses import asdict as _asdict
from typing import Any, Iterable, Tuple

from db.session import SessionLocal
from db.repos import pain_clusters as repo


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, "__dataclass_fields__"):
        return _asdict(obj).get(key, default)
    return getattr(obj, key, default)


def _normalize_title(s: Any) -> str:
    t = str(s or "").strip()
    if not t:
        t = "(untitled)"
    return t[:255]


def write_clusters(
    clusters: Iterable[Any],
    *,
    vertical_id: int,
    cluster_version: str,
) -> Tuple[int, int, int]:
    """
    Persist clusters idempotently.

    Accepts items that are dict-like OR objects with fields:
      - cluster_key
      - title
      - size

    Returns (inserted, updated, unchanged).
    """
    inserted = 0
    updated = 0
    unchanged = 0

    db = SessionLocal()
    try:
        for c in clusters:
            cluster_key = _get(c, "cluster_key")
            title = _normalize_title(_get(c, "title"))
            size = int(_get(c, "size", 0))

            _, was_inserted, was_updated = repo.upsert_cluster(
                db,
                vertical_id=int(vertical_id),
                cluster_version=str(cluster_version),
                cluster_key=str(cluster_key),
                title=title,
                size=size,
            )

            if was_inserted:
                inserted += 1
            elif was_updated:
                updated += 1
            else:
                unchanged += 1

        print(
            f"[clustering] vertical_id={vertical_id} cluster_version={cluster_version} "
            f"inserted={inserted} updated={updated} unchanged={unchanged}"
        )
        return inserted, updated, unchanged
    finally:
        db.close()
