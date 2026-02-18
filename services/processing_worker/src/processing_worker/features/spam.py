from domain.scoring.spam_score_v1 import compute_spam_score as _compute_spam_score


def compute_spam_score(content: str) -> int:
    return _compute_spam_score(content=content)
