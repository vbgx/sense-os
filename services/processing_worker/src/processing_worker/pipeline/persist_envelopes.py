from __future__ import annotations

from typing import Iterable

from processing_worker.models.signal_envelope import SignalEnvelope
from processing_worker.storage.pain_instances_writer import PainInstancesWriter
from processing_worker.storage.signals_features_writer import SignalsFeaturesWriter


def persist_envelopes(envelopes: Iterable[SignalEnvelope]) -> dict[str, int]:
    envs = list(envelopes)
    if not envs:
        return {"signals_updated": 0, "pain_instances_persisted": 0}

    signals_rows = []
    pain_instances = []

    for e in envs:
        signals_rows.append(
            {
                "signal_id": e.signal_id,
                "language_code": e.language_code,
                "spam_score": e.spam_score,
                "quality_score": e.quality_score,
                "vertical_auto_classification": e.vertical_auto,
            }
        )
        if e.pain_instance is not None:
            pain_instances.append(e.pain_instance)

    signals_updated = SignalsFeaturesWriter().update_many(signals_rows)

    pain_instances_persisted = 0
    if pain_instances:
        pain_instances_persisted = PainInstancesWriter().persist_many(pain_instances)

    return {
        "signals_updated": signals_updated,
        "pain_instances_persisted": pain_instances_persisted,
    }
