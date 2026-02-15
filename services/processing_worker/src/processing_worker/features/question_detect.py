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
