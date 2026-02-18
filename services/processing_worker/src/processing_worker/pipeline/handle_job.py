from __future__ import annotations

from typing import Any

from processing_worker.pipeline.load_signals import load_signals
from processing_worker.pipeline.persist_envelopes import persist_envelopes
from processing_worker.pipeline.process_batch import process_batch


def _summarize_timings(timings_ms: dict[str, list[float]]) -> dict[str, dict[str, float | int]]:
    """
    Compress high-volume per-item timings into stable aggregates.
    Keeps logs/script output readable while still useful.
    """
    out: dict[str, dict[str, float | int]] = {}
    for name, xs in (timings_ms or {}).items():
        if not isinstance(xs, list) or not xs:
            out[name] = {"n": 0, "sum_ms": 0.0, "avg_ms": 0.0, "max_ms": 0.0}
            continue
        vals = [float(v) for v in xs]
        s = float(sum(vals))
        n = int(len(vals))
        out[name] = {
            "n": n,
            "sum_ms": s,
            "avg_ms": (s / n) if n else 0.0,
            "max_ms": float(max(vals)) if n else 0.0,
        }
    return out


def handle_job(job: dict[str, Any]) -> dict[str, Any]:
    signals = load_signals(job)
    envelopes, feature_metrics = process_batch(job, signals)
    stats = persist_envelopes(envelopes)

    return {
        "loaded": len(signals),
        "envelopes": len(envelopes),
        **stats,
        "feature_metrics": {
            # 🔥 was: huge lists. now: compact aggregates.
            "timings_ms": _summarize_timings(feature_metrics.timings_ms),
            "errors": feature_metrics.errors,
            "nulls": feature_metrics.nulls,
        },
    }
