from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PainInstanceOut:
    signal_id: int
    algo_version: str
    pain_score: float
    breakdown: dict[str, Any]
