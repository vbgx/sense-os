from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceInputs:
    size: int
    intra_similarity: float | None  # 0..1
    silhouette_score: float | None  # -1..1
    noise_ratio: float | None       # 0..1


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def compute_confidence_score(inp: ConfidenceInputs) -> int:
    """
    Deterministic confidence score (0–100).

    Components:

    1) Size factor (0–25)
       - 0 if size < 3
       - scales to max at 30+
    2) Intra similarity (0–25)
       - direct 0..1 scaling
    3) Silhouette (0–25)
       - negative → 0
       - positive scaled
    4) Noise ratio penalty (0–25)
       - high noise reduces score

    Final score = sum components
    """

    # Size
    if inp.size <= 2:
        size_score = 0.0
    else:
        size_score = _clamp(inp.size / 30.0, 0.0, 1.0) * 25.0

    # Intra similarity
    sim = inp.intra_similarity if inp.intra_similarity is not None else 0.0
    sim_score = _clamp(sim, 0.0, 1.0) * 25.0

    # Silhouette
    sil = inp.silhouette_score if inp.silhouette_score is not None else 0.0
    sil = _clamp(sil, -1.0, 1.0)
    sil_score = max(0.0, sil) * 25.0

    # Noise penalty (inverse)
    noise = inp.noise_ratio if inp.noise_ratio is not None else 1.0
    noise = _clamp(noise, 0.0, 1.0)
    noise_score = (1.0 - noise) * 25.0

    total = size_score + sim_score + sil_score + noise_score

    return int(round(_clamp(total, 0.0, 100.0)))
