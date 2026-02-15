from pydantic import BaseModel


class PainInstanceOut(BaseModel):
    signal_id: int
    algo_version: str
    pain_score: float
    breakdown: dict
