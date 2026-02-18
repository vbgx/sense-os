from __future__ import annotations

from typing import Any

from processing_worker.features_registry.registry import FEATURES
from processing_worker.features_registry.types import FeatureContext
from processing_worker.models.signal_envelope import SignalEnvelope
from processing_worker.observability.feature_metrics import FeatureMetrics, timed_call


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

        pain_instance = {
            "signal_id": signal_id,
            "vertical_db_id": vertical_db_id,
            "taxonomy_version": taxonomy_version,
            "pain_score": results.get("pain_score"),
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
                pain_score=results.get("pain_score"),
                pain_instance=pain_instance,
            )
        )

    return envelopes, metrics
