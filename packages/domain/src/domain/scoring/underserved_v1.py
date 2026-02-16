from __future__ import annotations

from dataclasses import dataclass


UNDERSERVED_VERSION = "underserved_v1"


@dataclass(frozen=True)
class UnderservedResult:
    underserved_factor: int
    version: str


def _clamp_0_100(value: float) -> int:
    return max(0, min(100, int(round(value))))


def compute_underserved_factor_v1(
    *,
    competitive_density_score: int,
    ph_overlap_score: int,
    repo_density_score: int,
    keyword_saturation_score: int,
    competitive_heat_score: int,
) -> UnderservedResult:
    """
    Compute underserved factor (0–100).

    Formula v1:

    underserved_factor =
        100 - (
            0.3 * competitive_density_score +
            0.2 * ph_overlap_score +
            0.2 * repo_density_score +
            0.2 * keyword_saturation_score +
            0.1 * competitive_heat_score
        )

    All inputs expected in range 0–100.
    Deterministic.
    """

    weighted_competition = (
        0.3 * competitive_density_score
        + 0.2 * ph_overlap_score
        + 0.2 * repo_density_score
        + 0.2 * keyword_saturation_score
        + 0.1 * competitive_heat_score
    )

    raw_score = 100.0 - weighted_competition
    final_score = _clamp_0_100(raw_score)

    return UnderservedResult(
        underserved_factor=final_score,
        version=UNDERSERVED_VERSION,
    )

