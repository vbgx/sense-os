from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class SourceKind(str, Enum):
    BUILDERS_QA = "builders_qa"
    BUILDERS_CODE = "builders_code"
    BUILDERS_COMMUNITY = "builders_community"
    SOCIAL_FEDIVERSE = "social_fediverse"
    NEWS_RSS = "news_rss"
    NEWS_MACRO = "news_macro"
    KNOWLEDGE_MACRO = "knowledge_macro"
    RESEARCH = "research"


class SignalIntent(str, Enum):
    PAIN = "pain"
    SOLUTION = "solution"
    TREND = "trend"
    COMPETITION = "competition"
    EVIDENCE = "evidence"


@dataclass(frozen=True)
class SourceRef:
    kind: SourceKind
    name: str
    external_id: str
    url: Optional[str] = None
    extra: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True)
class RawSignal:
    source: SourceRef
    title: str
    body: str
    created_at: Optional[str] = None
    author: Optional[str] = None
    tags: tuple[str, ...] = ()
    intent: Optional[SignalIntent] = None
    score_hint: Optional[float] = None
    raw: Optional[Mapping[str, Any]] = None
