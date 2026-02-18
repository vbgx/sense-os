from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class DailyPoint:
    day: date
    count: float


History = Iterable[DailyPoint]
