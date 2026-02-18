from __future__ import annotations

import logging
import os
from typing import Any

from processing_worker.pipeline.load_signals import load_signals
from processing_worker.pipeline.persist_envelopes import persist_envelopes
from processing_worker.pipeline.process_batch import process_batch

log = logging.getLogger(__name__)


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


def _processing_debug_enabled() -> bool:
    return os.getenv("PROCESSING_DEBUG") == "1"


def _quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    if q <= 0:
        return float(sorted_vals[0])
    if q >= 1:
        return float(sorted_vals[-1])
    idx = int(round((len(sorted_vals) - 1) * q))
    return float(sorted_vals[max(0, min(idx, len(sorted_vals) - 1))])


def _get_threshold(job: dict[str, Any]) -> float:
    # best-effort: allow job override, then env, then default
    v = job.get("threshold_create_pain")
    if v is not None:
        try:
            return float(v)
        except Exception:
            pass
    ev = os.getenv("PAIN_CREATE_THRESHOLD")
    if ev:
        try:
            return float(ev)
        except Exception:
            pass
    return 0.5


def _log_pain_score_debug(job: dict[str, Any], envelopes: list[Any]) -> None:
    if not _processing_debug_enabled():
        return

    xs: list[float] = []
    rows: list[dict[str, Any]] = []
    for e in envelopes:
        ps = getattr(e, "pain_score", None)
        if ps is None:
            continue
        try:
            xs.append(float(ps))
        except Exception:
            continue

        # best-effort fields
        rows.append(
            {
                "signal_id": getattr(e, "signal_id", None),
                "external_id": getattr(e, "external_id", None),
                "source": getattr(e, "source", None),
                "title": (getattr(e, "title", None) or "")[:80],
                "pain_score": float(ps),
            }
        )

    xs_sorted = sorted(xs)
    threshold = _get_threshold(job)
    above = sum(1 for v in xs if v >= threshold)

    top = sorted(rows, key=lambda r: float(r.get("pain_score") or 0.0), reverse=True)[:5]

    log.info(
        "processing_debug pain_score min=%.4f p50=%.4f p90=%.4f max=%.4f threshold=%.4f above_threshold=%s n=%s vertical_db_id=%s run_id=%s day=%s",
        _quantile(xs_sorted, 0.0),
        _quantile(xs_sorted, 0.5),
        _quantile(xs_sorted, 0.9),
        _quantile(xs_sorted, 1.0),
        float(threshold),
        int(above),
        int(len(xs)),
        job.get("vertical_db_id"),
        job.get("run_id"),
        job.get("day") or job.get("start_day"),
    )

    for r in top:
        log.info(
            "processing_debug_top signal_id=%s external_id=%s source=%s pain_score=%.4f title=%s",
            r.get("signal_id"),
            r.get("external_id"),
            r.get("source"),
            float(r.get("pain_score") or 0.0),
            r.get("title"),
        )


def handle_job(job: dict[str, Any]) -> dict[str, Any]:
    signals = load_signals(job)
    envelopes, feature_metrics = process_batch(job, signals)

    # ✅ scoring observability
    _log_pain_score_debug(job, envelopes)

    stats = persist_envelopes(envelopes)

    return {
        "loaded": len(signals),
        "envelopes": len(envelopes),
        **stats,
        "feature_metrics": {
            "timings_ms": _summarize_timings(feature_metrics.timings_ms),
            "errors": feature_metrics.errors,
            "nulls": feature_metrics.nulls,
        },
    }
