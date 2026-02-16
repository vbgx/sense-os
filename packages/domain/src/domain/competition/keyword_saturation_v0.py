from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


_WORD_RE = re.compile(r"[a-z0-9]+")
_DEFAULT_FREQS = {
    "shopify": 0.9,
    "returns": 0.8,
    "refund": 0.7,
    "refunds": 0.7,
    "policy": 0.4,
    "support": 0.6,
    "workflow": 0.5,
    "automation": 0.6,
    "payouts": 0.5,
    "reconciliation": 0.4,
    "ecommerce": 0.6,
    "billing": 0.5,
    "subscriptions": 0.5,
}


@dataclass(frozen=True)
class KeywordSaturationResult:
    keyword_saturation_score: int
    matched_terms: list[str]
    avg_frequency: float


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall((text or "").lower()))


def _load_fixture_freqs(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        out: dict[str, float] = {}
        for k, v in raw.items():
            try:
                out[str(k).lower()] = float(v)
            except Exception:
                continue
        return out
    except Exception:
        return {}


def compute_keyword_saturation_score_v0(
    key_phrases: Sequence[str] | Iterable[str],
    fixture_path: Path,
) -> KeywordSaturationResult:
    """
    Simple saturation proxy based on average keyword frequency.
    """
    terms = _tokens(" ".join(key_phrases or []))
    freq_map = _load_fixture_freqs(fixture_path) or _DEFAULT_FREQS

    matched = sorted([t for t in terms if t in freq_map])
    if matched:
        avg = sum(freq_map[t] for t in matched) / float(len(matched))
    else:
        avg = 0.0

    score = int(round(max(0.0, min(1.0, avg)) * 100.0))
    return KeywordSaturationResult(
        keyword_saturation_score=score,
        matched_terms=matched,
        avg_frequency=float(avg),
    )
