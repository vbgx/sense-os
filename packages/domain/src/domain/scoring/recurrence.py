from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional


@dataclass(frozen=True)
class RecurrenceSignal:
    """
    Minimal view of a signal needed to compute recurrence.

    - user_id: stable per author within a source when possible (preferred).
    - source_id: fallback identity (platform native post id); not a user id.
    - created_at: datetime for temporal distribution.
    - text: raw text for repeated-phrase detection.
    """
    user_id: Optional[str] = None
    source_id: Optional[str] = None
    created_at: Optional[datetime] = None
    text: str = ""


_WORD_RE = re.compile(r"[a-z0-9]+")


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


def _normalize_text(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


def _ngrams(tokens: list[str], n: int) -> list[str]:
    if n <= 0 or len(tokens) < n:
        return []
    return [" ".join(tokens[i : i + n]) for i in range(0, len(tokens) - n + 1)]


def _repeat_phrase_coverage(signals: list[RecurrenceSignal]) -> float:
    """
    Returns [0..1] = how much of the cluster is covered by repeated phrases.
    Heuristic:
      - build 3-grams per signal (bounded)
      - count occurrences across signals (unique per-signal presence)
      - select repeated ngrams (present in >=2 signals)
      - compute share of signals that contain at least one repeated ngram
    """
    per_signal_ngrams: list[set[str]] = []
    ngram_doc_count: dict[str, int] = {}

    for s in signals:
        toks = _normalize_text(s.text)
        # bound per-signal extraction to avoid massive texts dominating CPU
        toks = toks[:400]
        grams = set(_ngrams(toks, 3))
        # bound number of grams stored
        if len(grams) > 800:
            grams = set(list(grams)[:800])
        per_signal_ngrams.append(grams)
        for g in grams:
            ngram_doc_count[g] = ngram_doc_count.get(g, 0) + 1

    repeated = {g for g, c in ngram_doc_count.items() if c >= 2}
    if not repeated:
        return 0.0

    covered = 0
    for grams in per_signal_ngrams:
        if grams.intersection(repeated):
            covered += 1

    return _clamp01(covered / float(len(signals))) if signals else 0.0


def _temporal_distribution_score(signals: list[RecurrenceSignal]) -> float:
    """
    Returns [0..1] measuring whether occurrences are time-distributed
    (not just a single-day spike).

    Heuristic:
      - bucket by UTC day
      - compute normalized entropy over day buckets (higher = more distributed)
      - multiply by (1 - max_share) to penalize spikes
    """
    buckets: dict[str, int] = {}
    for s in signals:
        if s.created_at is None:
            continue
        dt = s.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        key = dt.strftime("%Y-%m-%d")
        buckets[key] = buckets.get(key, 0) + 1

    if not buckets:
        return 0.0

    counts = list(buckets.values())
    total = float(sum(counts))
    if total <= 0:
        return 0.0

    probs = [c / total for c in counts]
    # entropy
    ent = 0.0
    for p in probs:
        if p > 0:
            ent -= p * math.log(p)
    # normalize by max entropy for k buckets
    k = len(probs)
    max_ent = math.log(k) if k > 1 else 0.0
    ent_norm = (ent / max_ent) if max_ent > 0 else 0.0

    max_share = max(probs) if probs else 1.0
    spike_penalty = 1.0 - max_share  # 0 when all on one day, approaches 1 when spread

    return _clamp01(ent_norm * spike_penalty)


def compute_recurrence(
    signals: Iterable[RecurrenceSignal],
    *,
    w_users: float = 0.50,
    w_phrases: float = 0.30,
    w_time: float = 0.20,
    cap_unique_users: float = 80.0,
) -> tuple[int, float]:
    """
    Returns (recurrence_score_0_100, recurrence_ratio_0_1).

    Components:
      - users: unique user count (log-normalized) + penalize single-user dominance
      - phrases: repeated-phrase coverage across signals
      - time: time-distributed occurrences score
    """
    items = list(signals)
    n = len(items)
    if n == 0:
        return 0, 0.0

    # Unique users: prefer user_id; fallback to source_id only as last resort (weak signal).
    user_keys = []
    for s in items:
        if s.user_id:
            user_keys.append(f"u:{s.user_id}")
        elif s.source_id:
            user_keys.append(f"s:{s.source_id}")
        else:
            user_keys.append("unknown")

    unique_users = len(set(user_keys))
    users_log = _log_norm(float(unique_users), cap_unique_users)

    # Dominance penalty: if 1 user contributes almost all signals, recurrence should be low.
    # Compute max share by user.
    counts_by_user: dict[str, int] = {}
    for k in user_keys:
        counts_by_user[k] = counts_by_user.get(k, 0) + 1
    max_share = max(counts_by_user.values()) / float(n) if n > 0 else 1.0
    dominance_penalty = 1.0 - _clamp01(max_share)  # 0 if one user = 100%, higher when diversified

    users_component = _clamp01(users_log * dominance_penalty)

    phrases_component = _repeat_phrase_coverage(items)
    time_component = _temporal_distribution_score(items)

    ratio = (
        w_users * users_component
        + w_phrases * phrases_component
        + w_time * time_component
    )
    ratio = _clamp01(ratio)

    return int(round(100.0 * ratio)), ratio
