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
