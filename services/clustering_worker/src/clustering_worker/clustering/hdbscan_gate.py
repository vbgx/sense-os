from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HdbscanGateDecision:
    should_optimize: bool
    reason: str


def decide_hdbscan_optimize(
    *,
    prev: dict[str, Any] | None,
    current_n: int,
    volume_change_threshold: float = 0.25,
    quality_drop_threshold: float = 0.10,
) -> HdbscanGateDecision:
    if prev is None:
        return HdbscanGateDecision(True, "no_previous_params")

    prev_n = int(prev.get("n_instances") or 0)
    prev_quality = float(prev.get("quality_score") or 0.0)
    current_quality = float(prev.get("current_quality_score") or prev_quality)

    if prev_n <= 0:
        return HdbscanGateDecision(True, "previous_volume_missing")

    change = abs(current_n - prev_n) / float(prev_n)

    if change >= volume_change_threshold:
        return HdbscanGateDecision(True, f"volume_change_{change:.3f}")

    if (prev_quality - current_quality) >= quality_drop_threshold:
        return HdbscanGateDecision(True, f"quality_drop_{(prev_quality - current_quality):.3f}")

    return HdbscanGateDecision(False, "reuse_previous_params")
