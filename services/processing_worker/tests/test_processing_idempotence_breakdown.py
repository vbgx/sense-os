from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Signal, Vertical
from db.repos import pain_instances as pain_instances_repo
from processing_worker.storage.dedup import breakdown_hash


def _make_session():
    """Create an in-memory SQLite session for idempotency tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _seed_vertical_with_signal(db, *, external_id: str) -> Signal:
    """Seed a vertical (if needed) and a signal tied to it."""
    vertical = db.query(Vertical).first()
    if vertical is None:
        vertical = Vertical(name="test-vertical")
        db.add(vertical)
        db.commit()
        db.refresh(vertical)

    signal = Signal(
        vertical_id=vertical.id,
        source="test",
        external_id=external_id,
        content="Example content",
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def test_breakdown_hash_is_stable_for_same_breakdown():
    """Same breakdown content should yield the same hash."""
    a = {"score": 1.25, "pain_hits": 2, "flags": {"x": True, "y": False}}
    b = {"pain_hits": 2, "flags": {"y": False, "x": True}, "score": 1.25}

    key_a = breakdown_hash(a)
    key_b = breakdown_hash(b)

    assert key_a == key_b


def test_create_if_absent_dedupes_on_algo_version_and_breakdown_hash():
    """Identical breakdowns should be deduped for the same algo_version."""
    db = _make_session()
    signal_a = _seed_vertical_with_signal(db, external_id="a")
    signal_b = _seed_vertical_with_signal(db, external_id="b")

    breakdown = {"score": 2.0, "pain_hits": 3}
    breakdown_h = breakdown_hash(breakdown)

    first, created_first = pain_instances_repo.create_if_absent(
        db,
        vertical_id=signal_a.vertical_id,
        signal_id=signal_a.id,
        algo_version="algo_v1",
        pain_score=2.0,
        breakdown=breakdown,
        breakdown_hash=breakdown_h,
    )

    second, created_second = pain_instances_repo.create_if_absent(
        db,
        vertical_id=signal_b.vertical_id,
        signal_id=signal_b.id,
        algo_version="algo_v1",
        pain_score=2.0,
        breakdown=breakdown,
        breakdown_hash=breakdown_h,
    )

    assert created_first is True
    assert created_second is False
    assert first.id == second.id

    different_breakdown = {"score": 3.5, "pain_hits": 1}
    third, created_third = pain_instances_repo.create_if_absent(
        db,
        vertical_id=signal_b.vertical_id,
        signal_id=signal_b.id,
        algo_version="algo_v1",
        pain_score=3.5,
        breakdown=different_breakdown,
        breakdown_hash=breakdown_hash(different_breakdown),
    )

    assert created_third is True
    assert third.id != first.id
