from __future__ import annotations

from typing import Iterable

import pytest

from db.models import ClusterSignal, PainCluster, PainInstance, Signal, Vertical
from processing_worker.storage.dedup import breakdown_hash
from clustering_worker.pipeline.run_clustering import run_clustering_job
from db.repos import cluster_signals as cluster_signals_repo


def _seed_pains(db_session, *, count: int = 3) -> Vertical:
    """Seed a vertical with signals and pain instances."""
    vertical = Vertical(name="vertical-cluster")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    for idx in range(count):
        signal = Signal(
            vertical_db_id=vertical.id,
            vertical_id=vertical.name,
            source="test",
            external_id=f"ext-{idx}",
            content=f"content {idx}",
        )
        db_session.add(signal)
        db_session.commit()
        db_session.refresh(signal)

        breakdown = {"score": 1.0 + idx, "signal_id": signal.id}
        pain = PainInstance(
            vertical_id=vertical.id,
            signal_id=signal.id,
            algo_version="algo_v1",
            pain_score=float(breakdown["score"]),
            breakdown=breakdown,
            breakdown_hash=breakdown_hash(breakdown),
        )
        db_session.add(pain)
        db_session.commit()

    return vertical


def _link_many_sqlite(db, *, cluster_id: int, pain_instance_ids: Iterable[int]) -> int:
    """SQLite-safe link implementation used for tests."""
    existing = {
        int(row[0])
        for row in db.query(ClusterSignal.pain_instance_id)
        .filter(ClusterSignal.cluster_id == int(cluster_id))
        .all()
    }
    inserted = 0
    for pid in pain_instance_ids:
        pid_i = int(pid)
        if pid_i in existing:
            continue
        db.add(ClusterSignal(cluster_id=int(cluster_id), pain_instance_id=pid_i))
        inserted += 1
    return inserted


@pytest.fixture()
def patch_link_many(monkeypatch):
    """Patch link_many to a SQLite-safe implementation for tests."""

    def _patched(db, *, cluster_id: int, pain_instance_ids):
        return _link_many_sqlite(db, cluster_id=cluster_id, pain_instance_ids=pain_instance_ids)

    monkeypatch.setattr(cluster_signals_repo, "link_many", _patched)


def test_cluster_job_processes_new_version(db_session, patch_link_many):
    """A new cluster_version should process and link pains."""
    vertical = _seed_pains(db_session, count=4)

    result = run_clustering_job(
        {"vertical_id": vertical.name, "vertical_db_id": vertical.id, "cluster_version": "tfidf_v1"}
    )

    assert result["clusters"] == 1
    assert result["pain_instances"] == 4
    assert result["links_inserted"] == 4

    clusters = (
        db_session.query(PainCluster)
        .filter(PainCluster.vertical_id == vertical.id)
        .filter(PainCluster.cluster_version == "tfidf_v1")
        .all()
    )
    assert len(clusters) == 1

    links = (
        db_session.query(ClusterSignal)
        .filter(ClusterSignal.cluster_id == clusters[0].id)
        .all()
    )
    assert len(links) == 4


def test_cluster_job_skips_existing_version(db_session, monkeypatch):
    """If clusters already exist for version, job should skip."""
    vertical = _seed_pains(db_session, count=2)
    existing = PainCluster(
        vertical_id=vertical.id,
        cluster_version="tfidf_v1",
        cluster_key="all",
        title="All pains",
        size=2,
    )
    db_session.add(existing)
    db_session.commit()

    calls = {"count": 0}

    def _patched(db, *, cluster_id: int, pain_instance_ids):
        calls["count"] += 1
        return 0

    monkeypatch.setattr(cluster_signals_repo, "link_many", _patched)

    result = run_clustering_job(
        {"vertical_id": vertical.name, "vertical_db_id": vertical.id, "cluster_version": "tfidf_v1"}
    )

    assert result["skipped"] == 1
    assert calls["count"] == 0
