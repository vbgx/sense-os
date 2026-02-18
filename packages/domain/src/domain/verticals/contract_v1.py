from __future__ import annotations

from typing import Any, Iterable

from domain.models.vertical import VerticalMeta, VerticalTier

_META_KEYS = {
    "audience",
    "function",
    "industry",
    "cluster",
    "member",
    "persona",
    "variant",
}


def _normalize_str(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        return v
    raise ValueError(f"meta.{field} must be a string or null")


def _unexpected_keys(meta: dict[str, Any]) -> Iterable[str]:
    for k in meta.keys():
        if k not in _META_KEYS:
            yield k


def validate_vertical_meta(meta: Any) -> VerticalMeta:
    if meta is None:
        return VerticalMeta()
    if isinstance(meta, VerticalMeta):
        return meta
    if not isinstance(meta, dict):
        raise ValueError("meta must be an object")

    extra = list(_unexpected_keys(meta))
    if extra:
        extra_sorted = ", ".join(sorted(extra))
        raise ValueError(f"meta has unexpected keys: {extra_sorted}")

    return VerticalMeta(
        audience=_normalize_str(meta.get("audience"), "audience"),
        function=_normalize_str(meta.get("function"), "function"),
        industry=_normalize_str(meta.get("industry"), "industry"),
        cluster=_normalize_str(meta.get("cluster"), "cluster"),
        member=_normalize_str(meta.get("member"), "member"),
        persona=_normalize_str(meta.get("persona"), "persona"),
        variant=_normalize_str(meta.get("variant"), "variant"),
    )


def validate_vertical_tier(tier: Any) -> VerticalTier:
    if isinstance(tier, VerticalTier):
        return tier
    if isinstance(tier, str):
        normalized = tier.strip().lower()
        for candidate in VerticalTier:
            if normalized == candidate.value:
                return candidate
    raise ValueError("tier must be one of: core, experimental, long_tail")


from typing import NotRequired, TypedDict


class RawSignal(TypedDict, total=False):
    source: str
    external_id: str
    title: NotRequired[str]
    content: str
    url: NotRequired[str]
    created_at: NotRequired[str]
    author: NotRequired[str]
    subreddit: NotRequired[str]
    score: NotRequired[int]
    comments: NotRequired[int]
    metadata: NotRequired[dict]
