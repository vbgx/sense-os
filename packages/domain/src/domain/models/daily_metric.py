from dataclasses import dataclass

@dataclass(frozen=True)
class DailyMetric:
    cluster_id: int
    date: str
    formula_version: str
    frequency: int = 0
    engagement: int = 0
    avg_score: float = 0.0
    source_count: int = 0
