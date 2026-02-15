from __future__ import annotations

from datetime import datetime, date

from db.models import ClusterDailyMetric, ClusterSignal, PainCluster, PainInstance, Signal, Vertical
from processing_worker.storage.dedup import breakdown_hash
from trend_worker.pipeline.compute_trends import compute_trends_job


def _seed_trend_data(db_session, *, day: date) -> None:
    """Seed minimal data needed for trend computation."""
    vertical = Vertical(name="vertical-trend")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    signal = Signal(
        vertical_id=vertical.id,
        source="test",
        external_id="ext-trend",
        content="trend content",
        ingested_at=datetime.combine(day, datetime.min.time()),
    )
    db_session.add(signal)
    db_session.commit()
    db_session.refresh(signal)

    breakdown = {"score": 3.2, "signal_id": signal.id}
    pain = PainInstance(
        vertical_id=vertical.id,
        signal_id=signal.id,
        algo_version="algo_v1",
        pain_score=3.2,
        breakdown=breakdown,
        breakdown_hash=breakdown_hash(breakdown),
    )
    db_session.add(pain)
    db_session.commit()
    db_session.refresh(pain)

    cluster = PainCluster(
        vertical_id=vertical.id,
        cluster_version="tfidf_v1",
        cluster_key="all",
        title="All pains",
        size=1,
    )
    db_session.add(cluster)
    db_session.commit()
    db_session.refresh(cluster)

    link = ClusterSignal(cluster_id=cluster.id, pain_instance_id=pain.id)
    db_session.add(link)
    db_session.commit()


def test_trend_upsert_idempotent(db_session):
    """Trend computation should upsert idempotently for the same day/version."""
    day = date(2026, 2, 15)
    _seed_trend_data(db_session, day=day)

    job = {
        "day": day.isoformat(),
        "formula_version": "formula_v1",
        "cluster_version": "tfidf_v1",
    }

    first = compute_trends_job(job)
    assert first["rows"] == 1
    assert first["upserted"] == 1

    second = compute_trends_job(job)
    assert second["rows"] == 1
    assert second["upserted"] == 1

    count = db_session.query(ClusterDailyMetric).count()
    assert count == 1
