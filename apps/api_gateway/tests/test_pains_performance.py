from __future__ import annotations

from time import perf_counter

from db.models import PainInstance, Signal, Vertical
from processing_worker.storage.dedup import breakdown_hash


def _seed_many_pains(db_session, *, count: int) -> tuple[Vertical, list[PainInstance]]:
    """Seed a vertical with many pains for timing tests."""
    vertical = Vertical(name=f"vertical-perf-{count}")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    pains: list[PainInstance] = []
    for idx in range(count):
        signal = Signal(
            vertical_id=vertical.id,
            source="test",
            external_id=f"ext-perf-{idx}",
            content=f"content perf {idx}",
        )
        db_session.add(signal)
        db_session.commit()
        db_session.refresh(signal)

        breakdown = {"score": 1.0 + (idx % 5), "signal_id": signal.id}
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
        db_session.refresh(pain)
        pains.append(pain)

    return vertical, pains


def test_pains_list_performance(client, db_session):
    """List endpoint should respond quickly for modest datasets."""
    vertical, _ = _seed_many_pains(db_session, count=120)

    start = perf_counter()
    response = client.get(f"/pains?vertical_id={vertical.id}&limit=50&offset=0")
    elapsed = perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2.0


def test_pains_detail_performance(client, db_session):
    """Detail endpoint should respond quickly."""
    _, pains = _seed_many_pains(db_session, count=60)

    start = perf_counter()
    response = client.get(f"/pains/{pains[0].id}")
    elapsed = perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1.0
