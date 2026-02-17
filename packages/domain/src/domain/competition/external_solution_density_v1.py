from __future__ import annotations

import re
from typing import Iterable, Sequence


_WORD_RE = re.compile(r"[a-z0-9]+")

_KNOWN_SOLUTIONS = {
    "shopify",
    "stripe",
    "klaviyo",
    "hubspot",
    "zapier",
    "salesforce",
    "intercom",
    "zendesk",
    "mailchimp",
    "quickbooks",
    "xero",
    "notion",
    "jira",
    "asana",
    "trello",
    "slack",
    "figma",
}


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall((text or "").lower()))


def compute_competitive_density_score(
    signals: Sequence[str] | Iterable[str],
    key_phrases: Sequence[str] | Iterable[str] | None = None,
) -> int:
    """
    Heuristic competitive density: % of signals mentioning known external solutions.
    Deterministic and stable across runs.
    """
    items = list(signals or [])
    if not items:
        return 0

    mentions = 0
    for s in items:
        if _tokens(s) & _KNOWN_SOLUTIONS:
            mentions += 1

    density = mentions / float(len(items))
    score = int(round(max(0.0, min(1.0, density)) * 100.0))
    return score
