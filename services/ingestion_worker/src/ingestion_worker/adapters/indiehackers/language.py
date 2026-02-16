from __future__ import annotations


def detect_language(text: str) -> str:
    if not text:
        return "unknown"

    sample = text.lower()

    if any(word in sample for word in ["the", "and", "is", "are", "how", "what"]):
        return "en"

    if any(word in sample for word in ["le", "la", "les", "est", "pourquoi"]):
        return "fr"

    return "unknown"
