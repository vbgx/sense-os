from __future__ import annotations

from typing import Any

from processing_worker.pipeline.load_signals import load_signals
from processing_worker.pipeline.persist_envelopes import persist_envelopes
from processing_worker.pipeline.process_batch import process_batch


def handle_job(job: dict[str, Any]) -> dict[str, Any]:
    signals = load_signals(job)
    envelopes, feature_metrics = process_batch(job, signals)
    stats = persist_envelopes(envelopes)

    return {
        "loaded": len(signals),
        "envelopes": len(envelopes),
        **stats,
        "feature_metrics": {
            "timings_ms": feature_metrics.timings_ms,
            "errors": feature_metrics.errors,
            "nulls": feature_metrics.nulls,
        },
    }
