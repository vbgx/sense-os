from __future__ import annotations


def apply_quality_multiplier(*, severity_0_100: float, signal_quality_0_100: float) -> float:
    q = max(0.0, min(100.0, float(signal_quality_0_100))) / 100.0
    mult = 0.70 + 0.30 * q
    out = float(severity_0_100) * mult
    return max(0.0, min(100.0, out))
