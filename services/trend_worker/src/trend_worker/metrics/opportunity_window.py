from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from domain.scoring.opportunity_window import OpportunityInputs, OpportunityResult, compute_opportunity_window
from trend_worker.metrics.momentum import DailyMomentum, compute_growth_momentum_score


@dataclass(frozen=True)
class OpportunityDaily:
    day: str
    count: int


def compute_opportunity_window_for_cluster(
    *,
    breakout_score: int,
    saturation_score: int,
    daily: Iterable[OpportunityDaily],
    half_life_days: Optional[float] = None,
    competitive_heat_score: Optional[int] = None,
) -> OpportunityResult:
    momentum = compute_growth_momentum_score([DailyMomentum(day=d.day, count=d.count) for d in daily])
    return compute_opportunity_window(
        OpportunityInputs(
            breakout_score=int(breakout_score),
            saturation_score=int(saturation_score),
            growth_momentum=int(momentum),
            half_life_days=half_life_days,
            competitive_heat_score=competitive_heat_score,
        )
    )
