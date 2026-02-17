import re

QUESTION_RE = re.compile(
    r"\?$|^(how|why|what|which|where|when|anyone|does anyone|is there)\b",
    re.I,
)


def is_question(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if "?" in t:
        return True
    return bool(QUESTION_RE.search(t))

# --- compatibility API for tests ---
from processing_worker.features.markers import has_question


def question_score(text: str) -> float:
    """
    Minimal deterministic heuristic:
    - 1.0 if the text looks like a question, else 0.0
    """
    return 1.0 if has_question(text) else 0.0
