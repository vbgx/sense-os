from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OpportunityWindowStatus(str, Enum):
    EARLY = "EARLY"
    PEAK = "PEAK"
    SATURATING = "SATURATING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class OpportunityInputs:
    breakout_score: int          # 0..100
    saturation_score: int        # 0..100
    growth_momentum: int         # 0..100 (proxy)
    half_life_days: float | None # optional (if known)


@dataclass(frozen=True)
class OpportunityResult:
    opportunity_window_score: int                 # 0..100
    opportunity_window_status: OpportunityWindowStatus


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _clamp100(x: float) -> int:
    if x < 0.0:
        return 0
    if x > 100.0:
        return 100
    return int(round(x))


def _norm(score_0_100: int) -> float:
    return _clamp01(float(max(0, min(100, int(score_0_100)))) / 100.0)


def compute_opportunity_window(inputs: OpportunityInputs) -> OpportunityResult:
    """
    Opportunity Window (0..100) and status classification.

    Intuition:
    - Early: breakout high, saturation low, momentum high
    - Peak: breakout moderate, saturation moderate, momentum moderate/high
    - Saturating: saturation high, breakout low, momentum low

    Half-life (if available) acts as a mild modifier:
    - Short half-life suggests quicker decay -> lower opportunity
    - Long half-life suggests durable tail -> higher opportunity

    This is not exploitability (no monetizability / competition).
    Pure timing window synthesis.
    """
    b = _norm(inputs.breakout_score)
    s = _norm(inputs.saturation_score)
    m = _norm(inputs.growth_momentum)

    # Half-life modifier (mild; bounded)
    hl_mod = 0.0
    if inputs.half_life_days is not None:
        # Normalize: <7 days is short, >60 is long.
        d = float(inputs.half_life_days)
        if d <= 0:
            hl_mod = -0.10
        elif d < 7:
            hl_mod = -0.08
        elif d < 14:
            hl_mod = -0.04
        elif d < 30:
            hl_mod = 0.00
        elif d < 60:
            hl_mod = 0.03
        else:
            hl_mod = 0.06

    # Core synthesis:
    # - reward breakout + momentum
    # - penalize saturation
    ratio = (0.45 * b) + (0.35 * m) + (0.20 * (1.0 - s))
    ratio = _clamp01(ratio + hl_mod)
    score = _clamp100(100.0 * ratio)

    # Decision matrix for status (explicit, readable thresholds)
    # EARLY: breakout strong + saturation low
    if inputs.breakout_score >= 65 and inputs.saturation_score <= 35 and inputs.growth_momentum >= 55:
        status = OpportunityWindowStatus.EARLY
    # SATURATING: saturation strong + breakout weak (momentum tends to be low too)
    elif inputs.saturation_score >= 65 and inputs.breakout_score <= 40:
        status = OpportunityWindowStatus.SATURATING
    # PEAK: everything else in the middle: opportunity exists but window is closing / stabilizing
    elif inputs.saturation_score <= 65 and inputs.breakout_score >= 40:
        status = OpportunityWindowStatus.PEAK
    else:
        status = OpportunityWindowStatus.UNKNOWN

    return OpportunityResult(
        opportunity_window_score=score,
        opportunity_window_status=status,
    )
