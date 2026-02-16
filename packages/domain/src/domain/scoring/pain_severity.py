from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class SeveritySignal:
    """
    Minimal, portable view of a 'pain signal' needed to compute severity.

    Expected ranges (best-effort):
    - sentiment_compound: [-1.0 .. +1.0] where negative = negative sentiment
    - upvotes/comments/replies: >= 0
    - text: raw text (used only for length proxy / specificity)
    """
    sentiment_compound: Optional[float] = None
    upvotes: int = 0
    comments: int = 0
    replies: int = 0
    text: str = ""


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _log_norm(x: float, cap: float) -> float:
    """
    Log-normalize x into [0,1] against a cap (soft saturation).
    """
    if cap <= 0:
        return 0.0
    return _clamp01(math.log1p(max(0.0, x)) / math.log1p(cap))


def compute_pain_severity_index(
    signals: Iterable[SeveritySignal],
    *,
    w_frequency: float = 0.35,
    w_intensity: float = 0.25,
    w_engagement: float = 0.25,
    w_specificity: float = 0.15,
    # caps chosen to stabilize score across typical early datasets
    cap_frequency: float = 200.0,
    cap_engagement: float = 5000.0,
    cap_specificity_len: float = 500.0,
) -> int:
    """
    Pain Severity Index (0..100), based on:
      - Frequency: number of signals in cluster
      - Intensity: negative sentiment magnitude
      - Engagement: (upvotes, comments, replies) proxy
      - Specificity: text length proxy

    The score is:
      score = 100 * (wF*F + wI*I + wE*E + wS*S)

    Notes:
    - Uses log-normalized proxies to prevent domination by outliers.
    - Intensity uses mean(max(0, -sentiment_compound)) (i.e., only negativity contributes).
    """
    items = list(signals)
    n = len(items)
    if n == 0:
        return 0

    # Frequency: log-normalized count
    frequency = _log_norm(float(n), cap_frequency)

    # Intensity: average negative magnitude (0..1), then clamp
    neg_vals = []
    for s in items:
        if s.sentiment_compound is None:
            continue
        neg_vals.append(max(0.0, -float(s.sentiment_compound)))
    if neg_vals:
        intensity = _clamp01(sum(neg_vals) / float(len(neg_vals)))
    else:
        intensity = 0.0

    # Engagement: weighted sum then log-normalized
    engagement_raw = 0.0
    for s in items:
        engagement_raw += float(max(0, s.upvotes))
        engagement_raw += 2.0 * float(max(0, s.comments))
        engagement_raw += 3.0 * float(max(0, s.replies))
    engagement = _log_norm(engagement_raw, cap_engagement)

    # Specificity: average log-normalized text length (capped)
    lengths = [len((s.text or "").strip()) for s in items]
    avg_len = float(sum(lengths)) / float(len(lengths)) if lengths else 0.0
    specificity = _log_norm(avg_len, cap_specificity_len)

    total = (
        w_frequency * frequency
        + w_intensity * intensity
        + w_engagement * engagement
        + w_specificity * specificity
    )
    total = _clamp01(total)

    return int(round(100.0 * total))
