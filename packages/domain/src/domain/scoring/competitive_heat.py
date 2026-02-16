from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CompetitiveHeatSignal:
    text: str


# v0 lexicon (expand iteratively; keep precision > recall)
COMPETITOR_MARKERS_STRONG = [
    "already solved by",
    "solved by",
    "we switched to",
    "we moved to",
    "migrated to",
    "replaced with",
    "instead of",
    "using ",
    "use ",
    "we use ",
    "we're using",
    "works with",
    "built-in",
    "out of the box",
    "native support",
    "feature already exists",
]

COMPETITOR_MARKERS_WEAK = [
    "alternative",
    "competitor",
    "similar tool",
    "like ",
    "equivalent",
    "substitute",
    "plugin",
    "integration",
]

# Common solution/tool words (generic, but often appear when people cite existing solutions)
SOLUTION_WORDS = [
    "tool",
    "product",
    "platform",
    "service",
    "saas",
    "app",
    "library",
    "framework",
    "plugin",
]


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _log_norm(x: float, cap: float) -> float:
    if cap <= 0:
        return 0.0
    return _clamp01(math.log1p(max(0.0, x)) / math.log1p(cap))


def _count_contains(text: str, markers: list[str]) -> int:
    t = (text or "").lower()
    return sum(1 for m in markers if m in t)


def compute_competitive_heat_score(
    signals: Iterable[CompetitiveHeatSignal],
    *,
    cap_hits: float = 20.0,
) -> int:
    """
    Competitive Heat Score (0..100), cluster-level.

    Proxy:
    - frequency of explicit mentions of existing solutions / alternatives
    - basic pattern matching (v0)

    Intuition:
    - Many "we switched to X / already solved by Y / use Z" => high competition heat
    - No explicit solution mentions => low heat

    Deterministic, bounded 0..100.
    """
    items = list(signals)
    if not items:
        return 0

    strong_hits = 0
    weak_hits = 0
    solution_word_hits = 0

    for s in items:
        t = s.text or ""
        strong_hits += 3 * _count_contains(t, COMPETITOR_MARKERS_STRONG)
        weak_hits += 1 * _count_contains(t, COMPETITOR_MARKERS_WEAK)
        solution_word_hits += 1 * _count_contains(t, SOLUTION_WORDS)

    # Strong markers dominate; weak markers and generic solution words add mild lift.
    raw = float(strong_hits) + 0.6 * float(weak_hits) + 0.25 * float(solution_word_hits)

    ratio = _log_norm(raw, cap_hits)
    return int(round(100.0 * ratio))
