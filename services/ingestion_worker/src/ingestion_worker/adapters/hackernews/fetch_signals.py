from __future__ import annotations

from typing import Any, Iterable


def fetch_hackernews_signals(*, vertical_id: str, query: str | None = None, limit: int = 50, **kwargs: Any) -> Iterable[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    q = (query or "").strip() or "saas"
    for i in range(int(limit)):
        items.append(
            {
                "vertical_db_id": int(kwargs.get("vertical_db_id") or 1),
                "taxonomy_version": str(kwargs.get("taxonomy_version") or "v1"),
                "source": "hackernews",
                "source_external_id": f"hn:{1000 + i}",
                "title": f"{q} item {i}",
                "text": f"sample text for {q} #{i}",
                "url": f"https://example.com/hn/{1000 + i}",
                "created_at": "2026-02-18T00:00:00Z",
                "author": "hn_user",
                "score": 1,
            }
        )
    return items
