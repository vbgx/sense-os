from __future__ import annotations

from pydantic import BaseModel
from typing import List


class BuildHypothesisOut(BaseModel):
    target_persona: str
    core_pain_statement: str
    suggested_micro_solution: str
    early_validation_path: str
    risk_flags: List[str]
