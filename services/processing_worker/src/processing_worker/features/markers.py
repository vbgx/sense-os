import re

QUESTION_RE = re.compile(r"\?$|^(how|why|what|which|where|when|anyone|does anyone|is there)\b", re.I)
PAIN_WORDS = [
    "pain", "struggle", "annoy", "frustrat", "hate", "issue", "problem", "broken", "impossible",
    "can't", "cannot", "won't", "hard", "difficult", "time-consuming", "waste", "expensive",
]
WORKAROUND_WORDS = ["workaround", "hack", "script", "manual", "spreadsheet", "excel", "google sheet", "copy paste"]
MONEY_WORDS = ["$", "usd", "eur", "€", "pricing", "price", "cost", "budget", "pay", "subscription"]


def has_question(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if "?" in t:
        return True
    return bool(QUESTION_RE.search(t))


def count_any(text: str, needles: list[str]) -> int:
    t = (text or "").lower()
    return sum(1 for n in needles if n in t)


def features(text: str) -> dict:
    t = text or ""
    return {
        "is_question": has_question(t),
        "pain_hits": count_any(t, PAIN_WORDS),
        "workaround_hits": count_any(t, WORKAROUND_WORDS),
        "money_hits": count_any(t, MONEY_WORDS),
        "len": len(t),
    }
