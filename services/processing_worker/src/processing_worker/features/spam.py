from __future__ import annotations

from domain.scoring.spam_score_v1 import compute_spam_score


def compute_spam(*, content: str) -> int:
    return compute_spam_score(content=content or "")
