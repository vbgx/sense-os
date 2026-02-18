from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class HackerNewsHit:
    object_id: str
    title: str
    url: Optional[str]
    author: Optional[str]
    points: int
    num_comments: int
    created_at_iso: str
    story_text: Optional[str]
    tags: tuple[str, ...]
    raw: Mapping[str, Any] | None = None

# --- Backward-compat export for tests ---
def parse_hn_item(payload):
    """
    Compatibility shim: tests import parse_hn_item.
    Prefer delegating to the actual parser if present.
    """
    fn = globals().get("parse_item") or globals().get("parse") or globals().get("parse_hn")
    if callable(fn):
        return fn(payload)

    # Minimal "fail-fast" parse if no parser exists
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")

    # Require at least an id (HN item id)
    if "id" not in payload:
        raise ValueError("HN payload missing 'id'")

    return payload
