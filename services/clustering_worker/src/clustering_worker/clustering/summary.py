from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

# v1: minimal stopwords & generic-garbage guards (keep small + deterministic)
_STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while",
    "to","of","in","on","for","with","from","at","by","as","into","over",
    "is","are","was","were","be","been","being",
    "it","this","that","these","those",
    "i","we","you","they","he","she","my","our","your","their",
    "not","no","yes","do","does","did","done",
    "can","could","should","would","will","may","might","must",
    "help","anyone","someone","pls","please","thanks","thx",
}

_GENERIC_BAD_PHRASES = {
    "general frustration",
    "general issue",
    "general problem",
    "need help",
    "any advice",
}

_GENERIC_BAD_TOKENS = {
    "problem","problems","issue","issues","frustration","frustrations","help","question",
    "anyone","someone","things","stuff","general","random","misc",
}

_PUNCT_RE = re.compile(r"[^a-zA-Z0-9\s\-_/]+")

# Simple brand/platform heuristics (v1): pick frequent capitalized tokens from raw texts.
# Keep conservative: we only extract "Shopify", "Stripe", "Notion", "Amazon", etc.
_CAP_TOKEN_RE = re.compile(r"\b[A-Z][a-zA-Z0-9]+\b")


@dataclass(frozen=True)
class SummaryInputs:
    """
    Inputs required to synthesize a stable, human-readable cluster summary.
    v1: rule-based, no LLM.
    """
    representative_texts: Sequence[str]
    dominant_persona: str | None = None  # e.g. "founder", "operator", "builder"
    top_ngrams: Sequence[str] | None = None  # optional: upstream extracted ngrams/titles


def _normalize_token(t: str) -> str:
    t = t.strip().lower()
    t = _PUNCT_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _tokenize(text: str) -> list[str]:
    text = _normalize_token(text)
    return [w for w in text.split(" ") if w and w not in _STOPWORDS]


def _ngrams(tokens: Sequence[str], n: int) -> list[str]:
    if n <= 0:
        return []
    out: list[str] = []
    for i in range(0, max(0, len(tokens) - n + 1)):
        gram = " ".join(tokens[i : i + n])
        out.append(gram)
    return out


def _count_phrases(texts: Iterable[str], max_tokens: int = 120) -> dict[str, int]:
    """
    Build simple frequency counts of unigrams/bigrams/trigrams from representative texts.
    Deterministic order later via sorting.
    """
    counts: dict[str, int] = {}
    for txt in texts:
        toks = _tokenize(txt)[:max_tokens]
        for n in (3, 2, 1):  # prefer longer phrases
            for g in _ngrams(toks, n):
                # skip generic tokens/phrases
                if g in _GENERIC_BAD_PHRASES:
                    continue
                if any(tok in _GENERIC_BAD_TOKENS for tok in g.split(" ")):
                    continue
                counts[g] = counts.get(g, 0) + 1
    return counts


def _pick_platform(texts: Iterable[str]) -> str | None:
    """
    v1 heuristic: platform = most frequent capitalized token among representative texts.
    """
    freq: dict[str, int] = {}
    for t in texts:
        for m in _CAP_TOKEN_RE.findall(t):
            # avoid trivial sentence-start capitalized words
            if len(m) < 3:
                continue
            if m.lower() in _STOPWORDS:
                continue
            freq[m] = freq.get(m, 0) + 1
    if not freq:
        return None
    # stable: count desc, token asc
    best = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return best


def _persona_phrase(dominant_persona: str | None) -> str:
    if not dominant_persona:
        return "Builders"
    p = dominant_persona.strip().lower()
    # keep minimal mapping (extend later)
    if p in {"founder", "founders"}:
        return "Founders"
    if p in {"operator", "ops", "operators"}:
        return "Operators"
    if p in {"builder", "builders"}:
        return "Builders"
    if p in {"dev", "developer", "developers"}:
        return "Developers"
    if p in {"marketer", "marketing"}:
        return "Marketers"
    return dominant_persona[:1].upper() + dominant_persona[1:]


def synthesize_cluster_summary(inp: SummaryInputs) -> str:
    """
    Output must be:
      - stable for identical inputs
      - non-empty
      - non-generic
    """
    texts = [t for t in inp.representative_texts if t and t.strip()]
    if not texts and inp.top_ngrams:
        # fallback if no texts: build from ngrams only
        core = inp.top_ngrams[0].strip() if inp.top_ngrams else ""
        core = core or "workflow friction"
        return f"{_persona_phrase(inp.dominant_persona)} struggle with {core}"

    texts = texts[:12]  # cap for determinism + cost
    platform = _pick_platform(texts)

    # phrase candidates: prefer upstream ngrams if provided, else compute from texts
    candidates: list[str] = []
    if inp.top_ngrams:
        candidates.extend([_normalize_token(x) for x in inp.top_ngrams if x and x.strip()])
    else:
        counts = _count_phrases(texts)
        # stable: count desc, phrase asc
        candidates.extend([k for k, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))])

    # choose best "core" phrase
    core = None
    for c in candidates:
        c = c.strip()
        if not c:
            continue
        if c in _GENERIC_BAD_PHRASES:
            continue
        # keep phrase length reasonable (avoid entire sentences)
        if len(c.split(" ")) > 7:
            continue
        if any(tok in _GENERIC_BAD_TOKENS for tok in c.split(" ")):
            continue
        core = c
        break

    if not core:
        core = "workflow friction"

    persona = _persona_phrase(inp.dominant_persona)

    # Compose (keep simple, readable)
    # Example: "Shopify Founders struggle with reconciliation mismatch after returns"
    if platform:
        return f"{platform} {persona} struggle with {core}"
    return f"{persona} struggle with {core}"
