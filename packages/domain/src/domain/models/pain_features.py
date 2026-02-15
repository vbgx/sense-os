from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureVector:
    is_question: bool
    sentiment: float
    pain_hits: int
    workaround_hits: int
    money_hits: int
    length: int
