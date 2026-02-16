from __future__ import annotations

from pydantic import BaseModel
from typing import List


class BuildSignalOut(BaseModel):
    recommendation: str
    reasoning_summary: str
    top_positive_factors: List[str]
    top_risk_factors: List[str]
