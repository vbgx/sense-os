from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, Optional

from domain.models.persona import Persona, PersonaInference
from domain.rules.persona_markers import PERSONA_MARKERS


@dataclass(frozen=True)
class PersonaSignal:
    text: str
    # optional metadata hooks for future (subreddit, title vs body, tags, etc.)
    source: Optional[str] = None


_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-\_]+")


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _normalize(text: str) -> str:
    return (text or "").lower()


def score_persona_for_signal(text: str) -> dict[Persona, float]:
    """
    Rule-based scoring per signal.
    Output is a raw (non-normalized) score per persona.
    """
    t = _normalize(text)
    raw: dict[Persona, float] = {p: 0.0 for p in Persona}

    if not t.strip():
        raw[Persona.unknown] = 1.0
        return raw

    # Token-level + substring markers (simple & stable).
    # We bias weights towards "strong" markers.
    for persona, buckets in PERSONA_MARKERS.items():
        strong = buckets.get("strong", [])
        weak = buckets.get("weak", [])

        for m in strong:
            if m in t:
                raw[persona] += 3.0
        for m in weak:
            if m in t:
                raw[persona] += 1.0

    # Light extra heuristics (still rule-based):
    # - Mention of "my saas" + "mrr" etc already captured.
    # - If nothing matched, call it unknown with small base.
    if all(raw[p] == 0.0 for p in Persona if p != Persona.unknown):
        raw[Persona.unknown] = 1.0

    return raw


def _softmax(scores: dict[Persona, float], temperature: float = 1.0) -> dict[Persona, float]:
    # Stable softmax
    vals = list(scores.values())
    m = max(vals) if vals else 0.0
    exps: dict[Persona, float] = {}
    denom = 0.0
    for k, v in scores.items():
        e = math.exp((v - m) / max(1e-6, temperature))
        exps[k] = e
        denom += e
    if denom <= 0:
        # fallback uniform
        n = len(scores) if scores else 1
        return {k: 1.0 / n for k in scores}
    return {k: exps[k] / denom for k in scores}


def infer_cluster_persona(
    signals: Iterable[PersonaSignal],
    *,
    temperature: float = 0.8,
    min_confidence: float = 0.30,
) -> PersonaInference:
    """
    Computes:
    - persona_distribution (0..1), cluster-level
    - dominant_persona
    - confidence (0..1)

    Confidence = top1_prob - top2_prob (margin),
    with a floor requirement to avoid overclaiming.
    """
    items = list(signals)
    if not items:
        dist = {Persona.unknown: 1.0}
        return PersonaInference(dominant_persona=Persona.unknown, confidence=0.0, distribution=dist)

    agg: dict[Persona, float] = {p: 0.0 for p in Persona}
    for s in items:
        per = score_persona_for_signal(s.text)
        for p, v in per.items():
            agg[p] += float(v)

    dist = _softmax(agg, temperature=temperature)

    # Determine top-2
    ranked = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)
    top1_p, top1 = ranked[0]
    top2 = ranked[1][1] if len(ranked) > 1 else 0.0

    confidence = _clamp01(top1 - top2)

    # Avoid overclaiming: if confidence too low, set unknown as dominant
    dominant = top1_p if confidence >= min_confidence and top1_p != Persona.unknown else Persona.unknown

    # If dominant forced to unknown, keep distribution intact for debugging
    return PersonaInference(dominant_persona=dominant, confidence=confidence, distribution=dist)
