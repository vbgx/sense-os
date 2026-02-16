cat > services/trend_worker/src/trend_worker/pipeline/load_clusters.py <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sqlalchemy.orm import Session

from db.models import PainCluster


@dataclass(frozen=True)
class LoadedCluster:
    id: str

    # EPIC 01
    severity_score: int
    recurrence_score: int
    monetizability_score: int
    contradiction_score: int

    # EPIC 02
    breakout_score: int
    saturation_score: int
    opportunity_window_score: int
    opportunity_window_status: str
    half_life_days: float | None
    competitive_heat_score: int


def load_clusters(session: Session) -> List[LoadedCluster]:
    """
    Load all clusters required for trend + exploitability computation.

    Deterministic.
    No filtering logic (v1).
    """

    rows = (
        session.query(PainCluster)
        .order_by(PainCluster.id.asc())
        .all()
    )

    result: List[LoadedCluster] = []

    for c in rows:
        result.append(
            LoadedCluster(
                id=c.id,

                severity_score=c.severity_score or 0,
                recurrence_score=c.recurrence_score or 0,
                monetizability_score=c.monetizability_score or 0,
                contradiction_score=c.contradiction_score or 0,

                breakout_score=c.breakout_score or 0,
                saturation_score=c.saturation_score or 0,
                opportunity_window_score=c.opportunity_window_score or 0,
                opportunity_window_status=c.opportunity_window_status or "UNKNOWN",
                half_life_days=c.half_life_days,
                competitive_heat_score=c.competitive_heat_score or 0,
            )
        )

    return result
EOF
