from __future__ import annotations

from typing import Any

from db.session import SessionLocal

from processing_worker.settings import ALGO_VERSION, SUPPORTED_LANGUAGES, SPAM_THRESHOLD
from processing_worker.features.extract_features import extract_features
from processing_worker.scoring import score_features
from processing_worker.pipeline.load_signals import load_batch
from processing_worker.pipeline.signal_envelope import SignalEnvelope
from processing_worker.pipeline.persist_signal_envelopes import persist_signal_envelopes_in_session
from processing_worker.storage.pain_instances_writer import write_pain_instances_bulk_in_session


def _extract_content(s: Any) -> str | None:
    content = (
        getattr(s, "content", None)
        or getattr(s, "text", None)
        or getattr(s, "body", None)
        or getattr(s, "title", None)
    )
    if not isinstance(content, str) or not content.strip():
        return None
    return content


def _build_envelope(s: Any, vertical_db_id: int) -> SignalEnvelope | None:
    content = _extract_content(s)
    if content is None:
        return None
    sid = getattr(s, "id", None)
    if sid is None:
        return None

    return SignalEnvelope(
        signal_id=int(sid),
        vertical_db_id=int(vertical_db_id),
        content=content,
        created_at=getattr(s, "created_at", None),
    )


def process_batch(*, signals: list[Any], vertical_db_id: int) -> dict[str, int]:
    envs: list[SignalEnvelope] = []
    skipped_empty = 0

    for s in signals:
        e = _build_envelope(s, vertical_db_id)
        if e is None:
            skipped_empty += 1
            continue
        envs.append(e)

    # compute + filter in-memory (deterministic, no DB roundtrips)
    supported = set(SUPPORTED_LANGUAGES)
    spam_threshold = int(SPAM_THRESHOLD)

    kept: list[SignalEnvelope] = []
    filtered = 0

    for e in envs:
        feats = extract_features(e.content)
        score, breakdown = score_features(feats)

        # best-effort extraction of common feature names
        language_code = feats.get("language_code") or feats.get("lang") or feats.get("language")
        spam_score = feats.get("spam_score") or feats.get("spam") or feats.get("spam_index")
        quality = feats.get("signal_quality") or feats.get("quality") or feats.get("quality_score")
        vertical_auto = feats.get("vertical_auto") or feats.get("vertical") or feats.get("vertical_auto_classification")

        # normalize
        lang = str(language_code) if language_code is not None else None
        spam = int(spam_score) if spam_score is not None else None
        qual = int(quality) if quality is not None else None
        vauto = str(vertical_auto) if vertical_auto is not None else None

        # filter policy (same as before, but no DB refresh)
        if lang is not None and lang not in supported:
            filtered += 1
            continue
        if spam is not None and spam >= spam_threshold:
            filtered += 1
            continue

        kept.append(
            SignalEnvelope(
                signal_id=e.signal_id,
                vertical_db_id=e.vertical_db_id,
                content=e.content,
                created_at=e.created_at,
                language_code=lang,
                spam_score=spam,
                signal_quality=qual,
                vertical_auto=vauto,
                pain_score=float(score),
                breakdown=breakdown,
            )
        )

    # Single DB session for all persistence
    db = SessionLocal()
    try:
        persist_signal_envelopes_in_session(db, kept)
        created, skipped = write_pain_instances_bulk_in_session(db=db, envelopes=kept, algo_version=str(ALGO_VERSION))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {
        "signals": int(len(signals)),
        "signals_skipped_empty": int(skipped_empty),
        "signals_filtered": int(filtered),
        "pain_instances_created": int(created),
        "pain_instances_skipped": int(skipped),
    }


def process_signals_batch(job: dict[str, Any]) -> dict[str, int]:
    vertical_db_id = int(job.get("vertical_db_id") or 0)
    if vertical_db_id <= 0:
        return {
            "signals": 0,
            "signals_skipped_empty": 0,
            "signals_filtered": 0,
            "pain_instances_created": 0,
            "pain_instances_skipped": 0,
        }

    limit = job.get("limit")
    offset = job.get("offset")

    # Defaults: process all current signals for the vertical (safe for V0)
    limit_i = int(limit) if isinstance(limit, int) else 500
    offset_i = int(offset) if isinstance(offset, int) else 0

    signals = load_batch(vertical_db_id=vertical_db_id, limit=limit_i, offset=offset_i)
    return process_batch(signals=signals, vertical_db_id=vertical_db_id)
