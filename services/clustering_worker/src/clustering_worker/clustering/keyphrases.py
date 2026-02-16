from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, Sequence


# Keep minimal & deterministic v1 stopwords.
_STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while",
    "to","of","in","on","for","with","from","at","by","as","into","over",
    "is","are","was","were","be","been","being",
    "it","this","that","these","those",
    "i","we","you","they","he","she","my","our","your","their",
    "not","no","yes","do","does","did","done",
    "can","could","should","would","will","may","might","must",
    "anyone","someone","pls","please","thanks","thx",
}

# Generic patterns to suppress v1
_GENERIC_PHRASES = {
    "need help",
    "any advice",
    "general issue",
    "general problem",
    "general frustration",
}

_GENERIC_TOKENS = {
    "problem","problems","issue","issues","help","question","anyone","someone","stuff","things","general",
    "frustration","frustrations",
}

# Keep punctuation stripping conservative; keep hyphen/underscore/slash as signal (csv-export, tax-reporting, etc.)
_PUNCT_RE = re.compile(r"[^a-zA-Z0-9\s\-_\/]+")
_WS_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class KeyPhrasesInputs:
    texts: Sequence[str]  # cluster docs (representative_signals texts preferred)
    top_k: int = 10
    max_docs: int = 12
    max_tokens_per_doc: int = 140


def _normalize(text: str) -> str:
    t = text.strip().lower()
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def _tokenize(text: str) -> list[str]:
    t = _normalize(text)
    toks = [w for w in t.split(" ") if w and w not in _STOPWORDS]
    # remove ultra-short tokens that are noise
    toks = [w for w in toks if len(w) >= 3]
    return toks


def _ngrams(tokens: Sequence[str], n: int) -> list[str]:
    if n <= 0:
        return []
    out: list[str] = []
    for i in range(0, max(0, len(tokens) - n + 1)):
        out.append(" ".join(tokens[i : i + n]))
    return out


def _is_generic_phrase(p: str) -> bool:
    if not p:
        return True
    if p in _GENERIC_PHRASES:
        return True
    parts = p.split(" ")
    if any(tok in _GENERIC_TOKENS for tok in parts):
        return True
    # avoid phrases that are basically stopwords / too short
    if len(parts) == 1 and len(parts[0]) < 4:
        return True
    return False


def _dedup_key(p: str) -> str:
    # Dedup trivial variants: collapse spaces, remove hyphens/underscores/slashes
    p = _normalize(p)
    p = p.replace("-", " ").replace("_", " ").replace("/", " ")
    p = _WS_RE.sub(" ", p).strip()
    return p


def extract_key_phrases(inp: KeyPhrasesInputs) -> list[str]:
    """
    TF-IDF intra-cluster:
      - Docs = representative texts (cap max_docs)
      - Candidate terms = 1-3 grams from tokenized docs
      - tf = raw count in doc
      - df = number of docs containing phrase
      - idf = log((N+1)/(df+1)) + 1
      - score(term) = sum_over_docs(tf_doc(term) * idf(term))
    Filters:
      - stopwords removal at token-level
      - generic phrase suppression
      - trivial dedup
      - cap phrase length
    Output:
      - top_k phrases, stable order for ties
    """
    docs = [t for t in inp.texts if isinstance(t, str) and t.strip()][: inp.max_docs]
    if not docs:
        return []

    # Build per-doc counts + df
    per_doc_counts: list[dict[str, int]] = []
    df: dict[str, int] = {}
    for d in docs:
        toks = _tokenize(d)[: inp.max_tokens_per_doc]
        counts: dict[str, int] = {}
        seen: set[str] = set()
        # prefer longer ngrams but include unigrams too
        for n in (3, 2, 1):
            for g in _ngrams(toks, n):
                if len(g.split(" ")) > 5:
                    continue
                if _is_generic_phrase(g):
                    continue
                counts[g] = counts.get(g, 0) + 1
                if g not in seen:
                    df[g] = df.get(g, 0) + 1
                    seen.add(g)
        per_doc_counts.append(counts)

    N = len(per_doc_counts)
    if N == 0:
        return []

    # Compute global scores
    scores: dict[str, float] = {}
    for term, dfi in df.items():
        idf = math.log((N + 1.0) / (dfi + 1.0)) + 1.0
        s = 0.0
        for c in per_doc_counts:
            tf = c.get(term, 0)
            if tf:
                s += float(tf) * idf
        scores[term] = s

    # Sort: score desc, df desc (more representative), term asc (stability)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], -df.get(kv[0], 0), kv[0]))

    # Dedup trivial variants and remove nested near-duplicates:
    # If "inventory mismatch" selected, skip "mismatch" if it shares the same dedup key subset.
    out: list[str] = []
    used_keys: set[str] = set()
    used_tokensets: list[set[str]] = []

    for term, _ in ranked:
        if len(out) >= inp.top_k:
            break
        t = term.strip()
        if not t:
            continue
        key = _dedup_key(t)
        if not key or key in used_keys:
            continue

        toks = set(key.split(" "))
        # skip if it is trivially contained in an already chosen phrase
        redundant = False
        for prev in used_tokensets:
            if toks.issubset(prev):
                redundant = True
                break
        if redundant:
            continue

        used_keys.add(key)
        used_tokensets.append(toks)
        out.append(t)

    return out


def extract_key_phrases_from_signals(
    signals: Iterable[dict],
    top_k: int = 10,
) -> list[str]:
    """
    Helper: extract key phrases from representative_signals list (preferred).
    Accepts signal dicts with text/content/body fields.
    """
    texts: list[str] = []
    for s in signals:
        if not isinstance(s, dict):
            continue
        t = s.get("text") or s.get("content") or s.get("body")
        if isinstance(t, str) and t.strip():
            texts.append(t)
    return extract_key_phrases(KeyPhrasesInputs(texts=texts, top_k=top_k))
