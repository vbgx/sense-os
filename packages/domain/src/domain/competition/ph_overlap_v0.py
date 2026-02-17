from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_WORD_RE = re.compile(r"[a-z0-9]+")
_DEFAULT_KEYWORDS = {
    "shopify",
    "ecommerce",
    "returns",
    "refund",
    "refunds",
    "reconciliation",
    "payments",
    "payouts",
    "billing",
    "subscriptions",
    "crm",
    "automation",
}


@dataclass(frozen=True)
class PHOverlapResult:
    ph_overlap_score: int
    similar_launch_count: int
    max_similarity: float


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall((text or "").lower()))


def _load_fixture_keywords(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keywords: set[str] = set()
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            for v in (obj.get("name"), obj.get("tagline"), obj.get("description")):
                if v:
                    keywords.update(_tokens(str(v)))
    except Exception:
        return set()
    return keywords


def compute_ph_overlap_score_v0(summary: str, fixture_path: Path) -> PHOverlapResult:
    """
    Cheap overlap proxy with optional fixture-driven keywords.
    """
    tokens = _tokens(summary)
    fixture_keywords = _load_fixture_keywords(fixture_path)
    keywords = fixture_keywords or _DEFAULT_KEYWORDS

    matched = tokens & keywords
    match_count = len(matched)

    similar_launch_count = min(10, match_count)
    max_similarity = max(0.0, min(1.0, match_count / 5.0))
    score = int(round(max(0.0, min(1.0, match_count / 4.0)) * 100.0))

    return PHOverlapResult(
        ph_overlap_score=score,
        similar_launch_count=int(similar_launch_count),
        max_similarity=float(max_similarity),
    )
