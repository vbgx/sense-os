from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


_WORD_RE = re.compile(r"[a-z0-9]+")
_DEFAULT_KEYWORDS = {
    "shopify",
    "refund",
    "refunds",
    "returns",
    "reconciliation",
    "payouts",
    "ecommerce",
    "payments",
    "billing",
    "subscriptions",
}


@dataclass(frozen=True)
class RepoDensityResult:
    repo_density_score: int
    matching_repo_count: int
    weighted_stars: float


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
            for v in (obj.get("name"), obj.get("description"), obj.get("topics")):
                if isinstance(v, list):
                    for item in v:
                        keywords.update(_tokens(str(item)))
                elif v:
                    keywords.update(_tokens(str(v)))
    except Exception:
        return set()
    return keywords


def compute_repo_density_score_v0(
    summary: str,
    key_phrases: Sequence[str] | Iterable[str],
    fixture_path: Path,
) -> RepoDensityResult:
    """
    Heuristic repo density proxy with optional fixture-driven keywords.
    """
    tokens = _tokens(summary) | _tokens(" ".join(key_phrases or []))
    fixture_keywords = _load_fixture_keywords(fixture_path)
    keywords = fixture_keywords or _DEFAULT_KEYWORDS

    matched = tokens & keywords
    match_count = len(matched)

    weighted_stars = float(match_count * 50.0)
    score = int(round(max(0.0, min(1.0, match_count / 3.0)) * 100.0))

    return RepoDensityResult(
        repo_density_score=score,
        matching_repo_count=int(match_count),
        weighted_stars=weighted_stars,
    )
