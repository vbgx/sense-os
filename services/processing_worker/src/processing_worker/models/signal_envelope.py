from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SignalEnvelope:
    signal_id: int
    vertical_db_id: int
    taxonomy_version: str
    language_code: str | None
    spam_score: float | None
    quality_score: float | None
    vertical_auto: dict[str, Any] | None
    pain_score: float | None
    pain_instance: dict[str, Any] | None

    # Optional: allow upstream to set it; if absent, writers will default.
    algo_version: str | None = None
