from __future__ import annotations

import logging
import os
from typing import Iterable

from processing_worker.models.signal_envelope import SignalEnvelope
from processing_worker.storage.pain_instances_writer import PainInstancesWriter
from processing_worker.storage.signals_features_writer import SignalsFeaturesWriter

log = logging.getLogger(__name__)


def _debug_enabled() -> bool:
    return os.getenv("PROCESSING_DEBUG") == "1" or os.getenv("SENSE_DEBUG") == "1"


def _ensure_pain_instance_shape(e: SignalEnvelope, raw: dict) -> dict:
    """
    Normalize pain_instance dict so the DB writer cannot silently drop it.

    Writer expects at least:
      - signal_id
      - vertical_db_id or vertical_id
      - pain_score
      - algo_version
      - breakdown (dict)
    """
    item = dict(raw or {})

    # Always set identifiers at root level
    item.setdefault("signal_id", int(e.signal_id))
    item.setdefault("vertical_db_id", int(e.vertical_db_id))
    item.setdefault("vertical_id", int(e.vertical_db_id))  # harmless alias

    # pain_score can live on envelope but missing in dict
    if item.get("pain_score") is None and e.pain_score is not None:
        item["pain_score"] = float(e.pain_score)

    # algo version default
    item.setdefault("algo_version", "heuristics_v1")

    # breakdown must exist and be a dict
    bd = item.get("breakdown")
    if not isinstance(bd, dict):
        bd = {}
    bd.setdefault("signal_id", int(e.signal_id))
    bd.setdefault("vertical_db_id", int(e.vertical_db_id))
    bd.setdefault("taxonomy_version", getattr(e, "taxonomy_version", None))
    item["breakdown"] = bd

    return item


def persist_envelopes(envelopes: Iterable[SignalEnvelope]) -> dict[str, int]:
    envs = list(envelopes)
    if not envs:
        return {"signals_updated": 0, "pain_instances_persisted": 0}

    signals_rows: list[dict] = []
    pain_instances: list[dict] = []

    # Debug counters (drop reasons before writer)
    dbg_missing_pi = 0

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

        if e.pain_instance is None:
            dbg_missing_pi += 1
            continue

        pain_instances.append(_ensure_pain_instance_shape(e, e.pain_instance))

    if _debug_enabled():
        sample = pain_instances[0] if pain_instances else None
        log.info(
            "persist_envelopes debug envs=%s pain_instances=%s missing_pain_instance=%s sample=%s",
            len(envs),
            len(pain_instances),
            dbg_missing_pi,
            sample,
        )

    signals_updated = SignalsFeaturesWriter().update_many(signals_rows)

    pain_instances_persisted = 0
    if pain_instances:
        pain_instances_persisted = PainInstancesWriter().persist_many(pain_instances)

    if _debug_enabled():
        log.info(
            "persist_envelopes debug signals_updated=%s pain_instances_persisted=%s",
            signals_updated,
            pain_instances_persisted,
        )

    return {
        "signals_updated": signals_updated,
        "pain_instances_persisted": pain_instances_persisted,
    }
