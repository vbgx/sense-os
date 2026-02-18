from domain.scoring.signal_quality import compute_signal_quality_score


def compute_signal_quality(content: str) -> int:
    return compute_signal_quality_score(content=content)
