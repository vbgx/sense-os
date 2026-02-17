from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from db.session import SessionLocal
from db.repos import cluster_daily_metrics as metrics_repo
from trend_worker.pipeline.persist_timeline_from_metrics import persist_timeline_from_trend_metrics

log = logging.getLogger(__name__)


def _default_day() -> date:
    return date.today() - timedelta(days=1)


def compute_trends_job(job: dict[str, Any]) -> dict[str, Any]:
    day_s = (job.get("day") or "").strip()
    try:
        d = date.fromisoformat(day_s) if day_s else _default_day()
    except Exception:
        d = _default_day()

    formula_version = str(job.get("formula_version") or "formula_v1")
    cluster_version = str(job.get("cluster_version") or "tfidf_v1")
    raw_vertical_id = job.get("vertical_id")
    vertical_id = None
    if raw_vertical_id not in (None, ""):
        try:
            vertical_id = int(raw_vertical_id)
        except Exception:
            vertical_id = None
    if vertical_id is not None and vertical_id <= 0:
        vertical_id = None

    db = SessionLocal()
    try:
        base_rows = metrics_repo.compute_for_day(
            db,
            d,
            formula_version=formula_version,
            cluster_version=cluster_version,
            vertical_id=vertical_id,
        )

        upserted = 0
        timeline_upserted = 0

        for r in base_rows:
            cluster_id = int(r["cluster_id"])
            frequency = int(r["frequency"])
            engagement = int(r["engagement"])
            avg_score = float(r["avg_score"])
            source_count = int(r["source_count"])

            prev = metrics_repo.get_prev_day(db, cluster_id=cluster_id, day=d, formula_version=formula_version)

            prev_freq = int(getattr(prev, "frequency", 0) or 0)
            velocity = 0.0
            if prev_freq > 0:
                velocity = (frequency - prev_freq) / float(prev_freq)

            emerging = max(0.0, velocity)
            declining = max(0.0, -velocity)

            # V0 scoring (simple, stable)
            score_volume = min(5.0, frequency / 10.0)
            score_velocity = max(-5.0, min(5.0, velocity * 5.0))
            score_novelty = 0.0
            score_diversity = min(5.0, float(source_count))
            score_confidence = 1.0 if frequency >= 3 else 0.5

            score = max(
                0.0,
                min(
                    5.0,
                    (avg_score * 0.6)
                    + (score_volume * 0.8)
                    + (max(0.0, score_velocity) * 0.6)
                    + (score_diversity * 0.2)
                    + (score_confidence * 0.2),
                ),
            )

            metrics_repo.upsert_metrics(
                db,
                cluster_id=cluster_id,
                day=d,
                formula_version=formula_version,
                frequency=frequency,
                engagement=engagement,
                avg_score=avg_score,
                source_count=source_count,
                velocity=float(velocity),
                emerging=float(emerging),
                declining=float(declining),
                score=float(score),
                score_volume=float(score_volume),
                score_velocity=float(score_velocity),
                score_novelty=float(score_novelty),
                score_diversity=float(score_diversity),
                score_confidence=float(score_confidence),
            )
            upserted += 1

            # EPIC 04 — ISSUE 04.04: timeline derived from trend metrics (frequency over time)
            # Coherent with trend metrics by construction, deterministic by compute_timeline().
            persist_timeline_from_trend_metrics(
                db,
                cluster_id=cluster_id,
                formula_version=formula_version,
                days=90,
            )
            timeline_upserted += 1

        log.info(
            "computed_trends day=%s formula_version=%s cluster_version=%s rows=%s upserted=%s timeline_clusters=%s",
            d.isoformat(),
            formula_version,
            cluster_version,
            len(base_rows),
            upserted,
            timeline_upserted,
        )
        return {
            "day": d.isoformat(),
            "rows": len(base_rows),
            "upserted": upserted,
            "timeline_clusters": timeline_upserted,
        }
    finally:
        db.close()


def compute_daily_metrics(*, day: date, job: dict[str, Any]) -> dict[str, Any]:
    """
    Public entrypoint used by the trend worker loop.
    """
    payload = dict(job)
    payload["day"] = day.isoformat()
    return compute_trends_job(payload)
