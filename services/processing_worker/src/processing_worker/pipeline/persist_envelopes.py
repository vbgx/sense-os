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

    signals_updated = SignalsFeaturesWriter().update_many(signals_rows)

    pain_instances_persisted = 0
    if pain_instances:
        pain_instances_persisted = PainInstancesWriter().persist_many(pain_instances)

    return {
        "signals_updated": signals_updated,
        "pain_instances_persisted": pain_instances_persisted,
    }
