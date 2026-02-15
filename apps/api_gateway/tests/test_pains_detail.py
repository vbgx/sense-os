from __future__ import annotations

from db.models import PainInstance, Signal, Vertical
from processing_worker.storage.dedup import breakdown_hash


def _seed_one_pain(db_session) -> PainInstance:
    """Create a single pain instance for detail tests."""
    vertical = Vertical(name="vertical-detail")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    signal = Signal(
        vertical_id=vertical.id,
        source="test",
        external_id="ext-detail",
        content="detail content",
    )
    db_session.add(signal)
    db_session.commit()
    db_session.refresh(signal)

    breakdown = {"score": 4.2, "signal_id": signal.id}
    pain = PainInstance(
        vertical_id=vertical.id,
        signal_id=signal.id,
        algo_version="algo_v1",
        pain_score=4.2,
        breakdown=breakdown,
        breakdown_hash=breakdown_hash(breakdown),
    )
    db_session.add(pain)
    db_session.commit()
    db_session.refresh(pain)

    return pain


def test_pains_detail_returns_item(client, db_session):
    """Detail endpoint returns a pain instance by id."""
    pain = _seed_one_pain(db_session)

    response = client.get(f"/pains/{pain.id}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["id"] == pain.id
    assert payload["algo_version"] == "algo_v1"


def test_pains_detail_not_found(client):
    """Detail endpoint returns 404 when missing."""
    response = client.get("/pains/999999")
    assert response.status_code == 404
