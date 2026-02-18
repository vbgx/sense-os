from __future__ import annotations

import logging
import os
from typing import Any

from processing_worker.features_registry.registry import FEATURES
from processing_worker.features_registry.types import FeatureContext
from processing_worker.models.signal_envelope import SignalEnvelope
from processing_worker.observability.feature_metrics import FeatureMetrics, timed_call

log = logging.getLogger(__name__)


def _debug_enabled() -> bool:
    return os.getenv("PROCESSING_DEBUG") == "1"


def _safe_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def _get_threshold(job: dict[str, Any]) -> float:
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


def _get_spam_threshold() -> float:
    ev = os.getenv("SPAM_THRESHOLD")
    if ev:
        try:
            return float(ev)
        except Exception:
            pass
    return 0.85


def _get_quality_min() -> float:
    ev = os.getenv("QUALITY_MIN")
    if ev:
        try:
            return float(ev)
        except Exception:
            pass
    return 0.25


def _quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    if q <= 0:
        return float(sorted_vals[0])
    if q >= 1:
        return float(sorted_vals[-1])
    idx = int(round((len(sorted_vals) - 1) * q))
    return float(sorted_vals[max(0, min(idx, len(sorted_vals) - 1))])


def process_batch(job: dict[str, Any], signals: list[dict[str, Any]]) -> tuple[list[SignalEnvelope], FeatureMetrics]:
    taxonomy_version = str(job["taxonomy_version"])
    vertical_db_id = int(job["vertical_db_id"])

    ctx = FeatureContext(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)
    metrics = FeatureMetrics()

    threshold = _get_threshold(job)
    spam_threshold = _get_spam_threshold()
    quality_min = _get_quality_min()

    algo_version = str(job.get("algo_version") or "heuristics_v1")

    # ✅ debug counters at the true decision point
    reasons: dict[str, int] = {
        "created": 0,
        "below_threshold": 0,
        "missing_pain_score": 0,
        "filtered_as_spam": 0,
        "quality_too_low": 0,
        "empty_content": 0,
    }
    top: list[dict[str, Any]] = []
    scores: list[float] = []

    envelopes: list[SignalEnvelope] = []

    for s in signals:
        signal_id = int(s["id"])
        text = str(s.get("text") or "")
        title = str(s.get("title") or "")
        content = f"{title}\n\n{text}".strip()

        if not content:
            reasons["empty_content"] += 1
            envelopes.append(
                SignalEnvelope(
                    signal_id=signal_id,
                    vertical_db_id=vertical_db_id,
                    taxonomy_version=taxonomy_version,
                    language_code=None,
                    spam_score=None,
                    quality_score=None,
                    vertical_auto=None,
                    pain_score=None,
                    pain_instance=None,
                )
            )
            continue

        results: dict[str, Any] = {}
        for spec in FEATURES:
            results[spec.name] = timed_call(metrics, spec.name, spec.fn, content=content, ctx=ctx)

        pain_score = _safe_float(results.get("pain_score"))
        spam_score = _safe_float(results.get("spam"))
        quality_score = _safe_float(results.get("quality"))

        if pain_score is not None:
            scores.append(float(pain_score))

        # ---- decision gate: create pain_instance or not ----
        create = True
        reason = "created"

        if spam_score is not None and spam_score >= spam_threshold:
            create = False
            reason = "filtered_as_spam"
        elif quality_score is not None and quality_score < quality_min:
            create = False
            reason = "quality_too_low"
        elif pain_score is None:
            create = False
            reason = "missing_pain_score"
        elif pain_score < threshold:
            create = False
            reason = "below_threshold"

        if create:
            # ✅ include breakdown + algo_version for idempotence + observability
            pain_instance = {
                "signal_id": signal_id,
                "vertical_db_id": vertical_db_id,
                "taxonomy_version": taxonomy_version,
                "algo_version": algo_version,
                "pain_score": float(pain_score),
                "breakdown": {
                    "algo_version": algo_version,
                    "threshold": float(threshold),
                    "pain_score": float(pain_score),
                    "spam_score": spam_score,
                    "quality_score": quality_score,
                    "features": results,  # heavy but audit-grade; if too big later, trim
                },
            }
            reasons["created"] += 1
        else:
            pain_instance = None
            reasons[reason] += 1

        # collect top signals for debug (only if pain_score exists)
        if _debug_enabled() and pain_score is not None:
            row = {
                "signal_id": signal_id,
                "pain_score": float(pain_score),
                "spam_score": spam_score,
                "quality_score": quality_score,
                "reason": reason,
                "title": title[:80],
            }
            top.append(row)
            top = sorted(top, key=lambda r: float(r.get("pain_score") or 0.0), reverse=True)[:5]

        envelopes.append(
            SignalEnvelope(
                signal_id=signal_id,
                vertical_db_id=vertical_db_id,
                taxonomy_version=taxonomy_version,
                language_code=results.get("language"),
                spam_score=results.get("spam"),
                quality_score=results.get("quality"),
                vertical_auto=results.get("vertical_auto"),
                pain_score=results.get("pain_score"),
                pain_instance=pain_instance,
            )
        )

    if _debug_enabled():
        xs = sorted(scores)
        log.info(
            "process_batch_debug n_signals=%s threshold=%.4f spam_threshold=%.4f quality_min=%.4f pain_score min=%.4f p50=%.4f p90=%.4f max=%.4f reasons=%s vertical_db_id=%s run_id=%s day=%s",
            len(signals),
            float(threshold),
            float(spam_threshold),
            float(quality_min),
            _quantile(xs, 0.0),
            _quantile(xs, 0.5),
            _quantile(xs, 0.9),
            _quantile(xs, 1.0),
            reasons,
            vertical_db_id,
            job.get("run_id"),
            job.get("day") or job.get("start_day"),
        )
        for r in top:
            log.info(
                "process_batch_top signal_id=%s pain_score=%.4f reason=%s spam=%s quality=%s title=%s",
                r.get("signal_id"),
                float(r.get("pain_score") or 0.0),
                r.get("reason"),
                r.get("spam_score"),
                r.get("quality_score"),
                r.get("title"),
            )

    return envelopes, metrics
