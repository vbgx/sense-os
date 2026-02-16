from __future__ import annotations

import re
from collections import Counter


_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_PROMO_RE = re.compile(r"\b(sign up|subscribe|buy now|limited offer|discount|use my code|promo code)\b", re.IGNORECASE)
_REPETITION_RE = re.compile(r"\b(\w+)\b")


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def compute_spam_score(*, content: str) -> int:
    text = content or ""
    n = len(text)

    if n == 0:
        return 100

    urls = len(_URL_RE.findall(text))
    promo_hits = len(_PROMO_RE.findall(text))

    words = _REPETITION_RE.findall(text.lower())
    repetition_ratio = 0.0
    if words:
        c = Counter(words)
        most_common = c.most_common(1)[0][1]
        repetition_ratio = most_common / max(len(words), 1)

    link_density = urls / max(len(words), 1)

    score01 = (
        0.35 * _clamp01(link_density * 10.0)
        + 0.30 * _clamp01(promo_hits / 3.0)
        + 0.35 * _clamp01(repetition_ratio * 5.0)
    )

    return int(round(_clamp01(score01) * 100.0))
