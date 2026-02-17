from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from domain.scoring.pain_severity import SeveritySignal, compute_pain_severity_index


@dataclass(frozen=True)
class InstanceForSeverity:
    """
    Adapter type for whatever your clustering pipeline carries around for instances.
    """
    text: str
    sentiment_compound: Optional[float]
    upvotes: int
    comments: int
    replies: int


def compute_cluster_severity(instances: Iterable[InstanceForSeverity]) -> int:
    signals = [
        SeveritySignal(
            text=i.text or "",
            sentiment_compound=i.sentiment_compound,
            upvotes=int(i.upvotes or 0),
            comments=int(i.comments or 0),
            replies=int(i.replies or 0),
        )
        for i in instances
    ]
    return compute_pain_severity_index(signals)
