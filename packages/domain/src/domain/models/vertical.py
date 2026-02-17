from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VerticalTier(str, Enum):
    CORE = "core"
    EXPERIMENTAL = "experimental"
    LONG_TAIL = "long_tail"


@dataclass(frozen=True)
class VerticalMeta:
    audience: str | None = None
    function: str | None = None
    industry: str | None = None
    cluster: str | None = None
    member: str | None = None
    persona: str | None = None
    variant: str | None = None


@dataclass(frozen=True)
class Vertical:
    vertical_id: str
    taxonomy_version: str
    meta: VerticalMeta
    tier: VerticalTier
