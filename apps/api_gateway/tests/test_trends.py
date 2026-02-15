from __future__ import annotations

from datetime import date, datetime

from db.models import ClusterDailyMetric, PainCluster, Vertical


def _seed_trend_rows(db_session, *, day: date) -> tuple[int, str, str]:
    """Seed clusters and daily metrics for trend endpoint tests."""
    vertical = Vertical(name="vertical-trends")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    cluster_a = PainCluster(
        vertical_id=vertical.id,
        cluster_version="tfidf_v1",
        cluster_key="a",
        title="Cluster A",
        size=3,
    )
    cluster_b = PainCluster(
        vertical_id=vertical.id,
        cluster_version="tfidf_v1",
        cluster_key="b",
        title="Cluster B",
        size=2,
    )
    db_session.add(cluster_a)
    db_session.add(cluster_b)
    db_session.commit()
    db_session.refresh(cluster_a)
    db_session.refresh(cluster_b)

    metrics = [
        ClusterDailyMetric(
            cluster_id=cluster_a.id,
            day=day,
            formula_version="formula_v1",
            frequency=10,
            engagement=10,
            avg_score=2.5,
            source_count=2,
            velocity=0.2,
            emerging=3.0,
            declining=0.1,
            score=3.2,
            score_volume=1.0,
            score_velocity=0.5,
            score_novelty=0.0,
            score_diversity=1.0,
            score_confidence=1.0,
            created_at=datetime.utcnow(),
        ),
        ClusterDailyMetric(
            cluster_id=cluster_b.id,
            day=day,
            formula_version="formula_v1",
            frequency=8,
            engagement=8,
            avg_score=2.0,
            source_count=1,
            velocity=0.8,
            emerging=1.5,
            declining=2.5,
            score=2.9,
            score_volume=0.8,
            score_velocity=1.2,
            score_novelty=0.0,
            score_diversity=0.8,
            score_confidence=0.8,
            created_at=datetime.utcnow(),
        ),
    ]
    db_session.add_all(metrics)
    db_session.commit()

    return vertical.id, str(cluster_a.id), str(cluster_b.id)


def test_trending_emerging_declining_pagination(client, db_session):
    """Trend endpoints should support pagination and stable ordering."""
    day = date(2026, 2, 15)
    vertical_id, cluster_a_id, cluster_b_id = _seed_trend_rows(db_session, day=day)

    trending = client.get(f"/trending?vertical_id={vertical_id}&day={day.isoformat()}&limit=10&offset=0")
    assert trending.status_code == 200
    payload = trending.json()
    assert payload["page"]["total"] == 2
    assert payload["page"]["limit"] == 10
    assert payload["page"]["offset"] == 0
    trending_ids = [item["cluster_id"] for item in payload["items"]]
    assert trending_ids == [cluster_a_id, cluster_b_id]

    emerging = client.get(f"/emerging?vertical_id={vertical_id}&day={day.isoformat()}&limit=10&offset=0")
    assert emerging.status_code == 200
    emerging_ids = [item["cluster_id"] for item in emerging.json()["items"]]
    assert emerging_ids == [cluster_b_id, cluster_a_id]

    declining = client.get(f"/declining?vertical_id={vertical_id}&day={day.isoformat()}&limit=10&offset=0")
    assert declining.status_code == 200
    declining_ids = [item["cluster_id"] for item in declining.json()["items"]]
    assert declining_ids == [cluster_b_id, cluster_a_id]

    paged = client.get(f"/trending?vertical_id={vertical_id}&day={day.isoformat()}&limit=1&offset=1")
    assert paged.status_code == 200
    paged_payload = paged.json()
    assert paged_payload["page"]["limit"] == 1
    assert paged_payload["page"]["offset"] == 1
    assert paged_payload["page"]["total"] == 2
    assert [item["cluster_id"] for item in paged_payload["items"]] == [cluster_b_id]
