from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> List[str]:
    return _WORD_RE.findall((text or "").lower())


def _tf(tokens: List[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    denom = float(len(tokens))
    return {k: v / denom for k, v in counts.items()}


def _idf(docs_tokens: List[List[str]]) -> Dict[str, float]:
    n = float(len(docs_tokens) or 1)
    df: Dict[str, int] = {}
    for toks in docs_tokens:
        seen = set(toks)
        for t in seen:
            df[t] = df.get(t, 0) + 1
    out: Dict[str, float] = {}
    for t, c in df.items():
        out[t] = math.log((n + 1.0) / (float(c) + 1.0)) + 1.0
    return out


def _tfidf(tf: Dict[str, float], idf: Dict[str, float]) -> Dict[str, float]:
    return {t: tfv * idf.get(t, 0.0) for t, tfv in tf.items() if tfv > 0.0}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = 0.0
    for k, av in a.items():
        bv = b.get(k)
        if bv is not None:
            dot += av * bv
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (na * nb)


@dataclass(frozen=True)
class VerticalDoc:
    key: str
    text: str


def _flatten_yaml(obj: object) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float, bool)):
        return str(obj)
    if isinstance(obj, list):
        return " ".join(_flatten_yaml(x) for x in obj)
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            parts.append(str(k))
            parts.append(_flatten_yaml(v))
        return " ".join(parts)
    return ""


def load_vertical_docs_from_dir(verticals_dir: Path) -> List[VerticalDoc]:
    docs: List[VerticalDoc] = []
    for p in sorted(verticals_dir.glob("*.yml")) + sorted(verticals_dir.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        key = data.get("id") or p.stem
        text = _flatten_yaml(data)
        docs.append(VerticalDoc(key=str(key), text=str(text)))
    return docs


def load_vertical_docs_default() -> List[VerticalDoc]:
    env_dir = os.environ.get("VERTICALS_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.exists() and p.is_dir():
            return load_vertical_docs_from_dir(p)

    candidates = [
        Path("/app/config/verticals"),
        Path("config/verticals"),
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return load_vertical_docs_from_dir(c)

    raise FileNotFoundError(
        "Vertical fixtures not found. Set VERTICALS_DIR or ensure config/verticals is available."
    )


@dataclass
class VerticalClassifierV1:
    vertical_docs: List[VerticalDoc]

    def __post_init__(self) -> None:
        corpus_tokens = [_tokens(d.text) for d in self.vertical_docs]
        self._idf = _idf(corpus_tokens)
        self._vertical_vecs: Dict[str, Dict[str, float]] = {}
        for d in self.vertical_docs:
            self._vertical_vecs[d.key] = _tfidf(_tf(_tokens(d.text)), self._idf)

    def classify(self, *, text: str) -> Tuple[str, float]:
        q = _tfidf(_tf(_tokens(text)), self._idf)
        best_key = "unknown"
        best_sim = 0.0
        for k, v in self._vertical_vecs.items():
            sim = _cosine(q, v)
            if sim > best_sim:
                best_sim = sim
                best_key = k
        return best_key, float(best_sim)


def classify_vertical_v1(
    *,
    content: str,
    threshold: float,
    classifier: VerticalClassifierV1,
) -> Tuple[str, int]:
    key, sim = classifier.classify(text=content or "")
    conf = int(round(max(0.0, min(1.0, sim)) * 100.0))
    if sim < float(threshold):
        return "unknown", conf
    return key, conf
