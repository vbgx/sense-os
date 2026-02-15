from dataclasses import dataclass

@dataclass(frozen=True)
class PainCluster:
    id: int
    vertical_id: int
    title: str
