from __future__ import annotations

from datetime import datetime
from typing import Optional

from domain.scoring.signal_quality import compute_signal_quality_score


def compute_quality(*, content: str, created_at: Optional[datetime]) -> int:
    return compute_signal_quality_score(content=content, created_at=created_at, engagement_norm01=None)
