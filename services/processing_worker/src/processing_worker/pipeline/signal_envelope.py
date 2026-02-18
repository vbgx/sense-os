from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class SignalEnvelope:
    signal_id: int
    vertical_db_id: int
    content: str
    created_at: Optional[datetime] = None

    # optional attributes we may persist back to Signal table
    language_code: Optional[str] = None
    spam_score: Optional[int] = None
    signal_quality: Optional[int] = None
    vertical_auto: Optional[str] = None

    # pain instance
    pain_score: Optional[float] = None
    breakdown: Optional[Any] = None
