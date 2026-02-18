from __future__ import annotations

import os
from typing import Any

from processing_worker.features_registry.registry import FEATURES
from processing_worker.features_registry.types import FeatureContext
from processing_worker.models.signal_envelope import SignalEnvelope
from processing_worker.observability.feature_metrics import FeatureMetrics, timed_call


def _debug_enabled() -> bool:
    return os.getenv("PROCESSING_DEBUG") == "1" or os.getenv("SENSE_DEBUG") == "1"


def _normalize_pain_score(value: Any) -> tuple[float | None, dict[str, Any] | None]:
    """
    Accepts:
      - float/int -> (float, None)
      - dict with common keys -> (float, breakdown)
    """
    if value is None:
        return None, None

    if isinstance(value, (int, float)):
        return float(value), None

    if isinstance(value, dict):
        # accept a few common shapes
        for k in ("score", "pain_score", "value", "combined"):
            v = value.get(k)
            if isinstance(v, (int, float)):
                breakdown = value.get("breakdown")
                if isinstance(breakdown, dict):
                    return float(v), breakdown
                return float(v), dict(value)
        # no numeric score found
        return None, dict(value)

    return None, None


def process_batch(job: dict[str, Any], signals: list[dict[str, Any]]) -> tuple[list[SignalEnvelope], FeatureMetrics]:
    taxonomy_version = str(job["taxonomy_version"])
    vertical_db_id = int(job["vertical_db_id"])

    ctx = FeatureContext(vertical_db_id=vertical_db_id, taxonomy_version=taxonomy_version)
    metrics = FeatureMetrics()

    envelopes: list[SignalEnvelope] = []

    for s in signals:
        signal_id = int(s["id"])
        text = str(s.get("text") or "")
        title = str(s.get("title") or "")
        content = f"{title}\n\n{text}".strip()

        results: dict[str, Any] = {}
        for spec in FEATURES:
            results[spec.name] = timed_call(metrics, spec.name, spec.fn, content=content, ctx=ctx)

        pain_score_raw = results.get("pain_score")
        pain_score, pain_breakdown = _normalize_pain_score(pain_score_raw)

        # ✅ DEBUG SAFETY NET: if pain_score is missing, still write rows so pipeline is unblocked.
        if pain_score is None and _debug_enabled():
            pain_score = 0.0
            if pain_breakdown is None:
                pain_breakdown = {}
            pain_breakdown.setdefault("debug", {})
            pain_breakdown["debug"]["pain_score_missing"] = True
            pain_breakdown["debug"]["pain_score_raw"] = str(pain_score_raw)[:500]

        pain_instance = {
            "signal_id": signal_id,
            "vertical_db_id": vertical_db_id,
            "taxonomy_version": taxonomy_version,
            "algo_version": str(job.get("algo_version") or "heuristics_v1"),
            "pain_score": pain_score,
            "breakdown": pain_breakdown or {"signal_id": signal_id},
        }

        envelopes.append(
            SignalEnvelope(
                signal_id=signal_id,
                vertical_db_id=vertical_db_id,
                taxonomy_version=taxonomy_version,
                language_code=results.get("language"),
                spam_score=results.get("spam"),
                quality_score=results.get("quality"),
                vertical_auto=results.get("vertical_auto"),
                pain_score=pain_score,
                pain_instance=pain_instance,
            )
        )

    return envelopes, metrics
