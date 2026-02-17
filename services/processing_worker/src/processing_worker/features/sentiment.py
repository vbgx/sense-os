"""
V0 sentiment stub.
Later: integrate VADER or similar.
"""

def simple_sentiment_score(text: str) -> float:
    # crude heuristic: more negative words -> more negative score
    NEG = ["hate", "annoy", "frustrat", "problem", "broken", "hard"]
    t = (text or "").lower()
    hits = sum(1 for n in NEG if n in t)
    return -0.2 * hits

# --- compatibility API for tests ---
import re


_NEG = [
    "pain", "struggle", "annoy", "frustrat", "hate", "issue", "problem", "broken", "impossible",
    "can't", "cannot", "won't", "hard", "difficult", "time-consuming", "waste", "expensive",
]
_POS = ["love", "great", "awesome", "nice", "good", "amazing", "perfect", "works"]


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def sentiment_score(text: str) -> float:
    """
    Deterministic, dependency-free heuristic sentiment.
    Returns a score in [0, 5] where higher means more negative/complaint-like.
    """
    t = (text or "").strip().lower()
    if not t:
        return 0.0

    neg = sum(1 for w in _NEG if w in t)
    pos = sum(1 for w in _POS if w in t)

    # punctuation emphasis
    ex = t.count("!")
    q = t.count("?")

    raw = 0.8 * neg - 0.5 * pos + 0.1 * ex + 0.05 * q
    return round(_clamp(raw, 0.0, 5.0), 2)
