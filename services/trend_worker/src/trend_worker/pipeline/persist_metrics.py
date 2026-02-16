from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from db.models import PainCluster
from domain.scoring.exploitability import ExploitabilityInputs, compute_exploitability


@dataclass(frozen=True)
class PersistableClusterMetrics:
    # Identity
    cluster_id: str

    # EPIC 01 (already on cluster; required for exploitability)
    severity_score: int
    recurrence_score: int
    monetizability_score: int
    contradiction_score: int

    # EPIC 02 (trend metrics)
    breakout_score: int
    saturation_score: int
    opportunity_window_score: int
    opportunity_window_status: str
    half_life_days: Optional[float]

    # EPIC 02.05 (competition)
    competitive_heat_score: int


def persist_metrics(session: Session, metrics: PersistableClusterMetrics) -> None:
    """
    Persist cluster trend metrics (EPIC 02) AND exploitability breakdown (EPIC 03).

    Contract:
    - deterministic
    - single DB update statement per cluster
    - exploitability_v1 computed from current metrics inputs
    """
    r = compute_exploitability(
        ExploitabilityInputs(
            severity_score=metrics.severity_score,
            recurrence_score=metrics.recurrence_score,
            monetizability_score=metrics.monetizability_score,
            breakout_score=metrics.breakout_score,
            opportunity_window_score=metrics.opportunity_window_score,
            half_life_days=metrics.half_life_days,
            contradiction_score=metrics.contradiction_score,
            competitive_heat_score=metrics.competitive_heat_score,
            saturation_score=metrics.saturation_score,
        )
    )

    stmt = (
        update(PainCluster)
        .where(PainCluster.id == metrics.cluster_id)
        .values(
            # EPIC 02
            breakout_score=int(metrics.breakout_score),
            saturation_score=int(metrics.saturation_score),
            opportunity_window_score=int(metrics.opportunity_window_score),
            opportunity_window_status=str(metrics.opportunity_window_status),
            half_life_days=metrics.half_life_days,
            competitive_heat_score=int(metrics.competitive_heat_score),

            # EPIC 03
            exploitability_score=int(r.exploitability_score),
            exploitability_pain_strength=float(r.breakdown.pain_strength),
            exploitability_timing_strength=float(r.breakdown.timing_strength),
            exploitability_risk_penalty=float(r.breakdown.risk_penalty),
            exploitability_version=str(r.exploitability_version),
            exploitability_tier=str(r.exploitability_tier.value),
        )
    )

    session.execute(stmt)
