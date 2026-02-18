from __future__ import annotations

import logging
import os
from typing import Any, Iterable

from processing_worker.models.signal_envelope import SignalEnvelope
from processing_worker.storage.pain_instances_writer import PainInstancesWriter
from processing_worker.storage.signals_features_writer import SignalsFeaturesWriter

log = logging.getLogger(__name__)


def _debug_enabled() -> bool:
    return os.getenv("PROCESSING_DEBUG") == "1"


def _get_threshold() -> float:
    v = os.getenv("PAIN_CREATE_THRESHOLD")
    if not v:
        return 0.5
    try:
        return float(v)
    except Exception:
        return 0.5


def _safe_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def persist_envelopes(envelopes: Iterable[SignalEnvelope]) -> dict[str, int]:
    envs = list(envelopes)
    if not envs:
        return {"signals_updated": 0, "pain_instances_persisted": 0}

    signals_rows: list[dict[str, Any]] = []
    pain_instances: list[dict[str, Any]] = []

    # ✅ debug: reason counters for "why pain_instance is None"
    reasons: dict[str, int] = {
        "has_pain_instance": 0,
        "below_threshold": 0,
        "filtered_as_spam": 0,
        "quality_too_low": 0,
        "missing_pain_score": 0,
        "missing_breakdown": 0,
        "unknown": 0,
    }
    examples: dict[str, list[dict[str, Any]]] = {k: [] for k in reasons.keys()}
    threshold = _get_threshold()

    for e in envs:
        vertical_auto = e.vertical_auto
        vertical_auto_id = None
        vertical_auto_conf = None
        if isinstance(vertical_auto, dict):
            vertical_auto_id = vertical_auto.get("id") or vertical_auto.get("vertical_id") or vertical_auto.get("name")
            vertical_auto_conf = vertical_auto.get("confidence")
        elif isinstance(vertical_auto, (list, tuple)) and len(vertical_auto) >= 2:
            vertical_auto_id = vertical_auto[0]
            vertical_auto_conf = vertical_auto[1]
        else:
            vertical_auto_id = vertical_auto

        signals_rows.append(
            {
                "signal_id": e.signal_id,
                "language_code": e.language_code,
                "spam_score": e.spam_score,
                "signal_quality_score": e.quality_score,
                "vertical_auto": vertical_auto_id,
                "vertical_auto_confidence": vertical_auto_conf,
            }
        )

        if e.pain_instance is not None:
            pain_instances.append(e.pain_instance)
            reasons["has_pain_instance"] += 1
            continue

        # If no pain_instance, try to explain why (best-effort)
        ps = _safe_float(getattr(e, "pain_score", None))
        spam = _safe_float(getattr(e, "spam_score", None))
        qual = _safe_float(getattr(e, "quality_score", None))
        breakdown = getattr(e, "breakdown", None)

        # Heuristic ordering: spam -> quality -> missing -> below threshold -> unknown
        reason = "unknown"

        # spam gate (assume [0..1], higher = more spam)
        spam_thr = os.getenv("SPAM_THRESHOLD")
        spam_threshold = _safe_float(spam_thr) if spam_thr else 0.85
        if spam is not None and spam_threshold is not None and spam >= spam_threshold:
            reason = "filtered_as_spam"

        # quality gate (assume [0..1], lower = worse)
        qual_thr = os.getenv("QUALITY_MIN")
        quality_min = _safe_float(qual_thr) if qual_thr else 0.25
        if reason == "unknown" and qual is not None and quality_min is not None and qual < quality_min:
            reason = "quality_too_low"

        if reason == "unknown" and ps is None:
            reason = "missing_pain_score"

        if reason == "unknown" and breakdown is None:
            reason = "missing_breakdown"

        if reason == "unknown" and ps is not None and ps < threshold:
            reason = "below_threshold"

        reasons[reason] += 1

        if _debug_enabled() and len(examples[reason]) < 3:
            examples[reason].append(
                {
                    "signal_id": getattr(e, "signal_id", None),
                    "source": getattr(e, "source", None),
                    "external_id": getattr(e, "external_id", None),
                    "title": (getattr(e, "title", None) or "")[:80],
                    "pain_score": ps,
                    "spam_score": spam,
                    "quality_score": qual,
                }
            )

    signals_updated = SignalsFeaturesWriter().update_many(signals_rows)

    pain_instances_persisted = 0
    if pain_instances:
        pain_instances_persisted = PainInstancesWriter().persist_many(pain_instances)

    # ✅ One-line killer summary
    if _debug_enabled():
        log.info(
            "persist_debug envelopes=%s threshold=%.4f pain_instances_persisted=%s reasons=%s",
            len(envs),
            float(threshold),
            int(pain_instances_persisted),
            reasons,
        )
        # Optional: a few concrete examples per reason (max 3)
        for k, xs in examples.items():
            if xs:
                log.info("persist_debug_examples reason=%s examples=%s", k, xs)

    return {
        "signals_updated": signals_updated,
        "pain_instances_persisted": pain_instances_persisted,
    }
