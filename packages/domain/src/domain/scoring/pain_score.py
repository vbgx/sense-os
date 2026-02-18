from __future__ import annotations

from typing import Any


def compute(*args: Any, **kwargs: Any) -> float:
    fn = globals().get("compute_pain_score") or globals().get("score") or globals().get("pain_score")
    if callable(fn) and fn is not compute:
        return float(fn(*args, **kwargs))

    val = kwargs.get("pain_score")
    if isinstance(val, (int, float)):
        return float(val)

    features = kwargs.get("features") or (args[0] if args else None)
    if isinstance(features, dict):
        x = features.get("pain_score")
        if isinstance(x, (int, float)):
            return float(x)
        x = features.get("severity_score")
        if isinstance(x, (int, float)):
            return float(x)

    return 0.0
