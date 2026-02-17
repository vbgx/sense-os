from __future__ import annotations

from datetime import date
from pydantic import BaseModel


class TimelinePointOut(BaseModel):
    date: date
    volume: int
    growth_rate: float
    velocity: float
    breakout_flag: bool
