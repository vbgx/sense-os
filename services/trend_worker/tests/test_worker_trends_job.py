from __future__ import annotations

from datetime import date, datetime

from db.models import ClusterSignal, PainCluster, PainInstance, Signal, Vertical
from processing_worker.storage.dedup import breakdown_hash
from trend_worker.main import consume_trend_job


def _seed_trend_data(db_session, *, day: date) -> None:
    """Seed minimal data needed for trend job consumption."""
    vertical = Vertical(name="vertical-trend-job")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    signal = Signal(
        vertical_db_id=vertical.id,
        vertical_id=vertical.name,
        source="test",
        external_id="ext-trend-job",
        content="trend content",
        ingested_at=datetime.combine(day, datetime.min.time()),
    )
    db_session.add(signal)
    db_session.commit()
    db_session.refresh(signal)

    breakdown = {"score": 2.8, "signal_id": signal.id}
    pain = PainInstance(
        vertical_id=vertical.id,
        signal_id=signal.id,
        algo_version="algo_v1",
        pain_score=2.8,
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

    db_session.add(ClusterSignal(cluster_id=cluster.id, pain_instance_id=pain.id))
    db_session.commit()


def test_consume_trend_job(db_session):
    """Trend worker should accept and process trend_job payloads."""
    day = date(2026, 2, 15)
    _seed_trend_data(db_session, day=day)

    payload = {
        "type": "trend_job",
        "day": day.isoformat(),
        "vertical_id": "vertical-trend-job",
        "vertical_db_id": 1,
        "taxonomy_version": "2026-02-17",
        "cluster_version": "tfidf_v1",
        "formula_version": "formula_v1",
    }

    result = consume_trend_job(payload)
    assert result is not None
    assert result.get("day") == day.isoformat()
    assert result.get("rows") == 1
    assert result.get("upserted") == 1
