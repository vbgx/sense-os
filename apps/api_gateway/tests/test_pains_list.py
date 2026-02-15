from __future__ import annotations

from typing import List, Tuple

from db.models import PainInstance, Signal, Vertical
from processing_worker.storage.dedup import breakdown_hash


def _seed_pains(db_session) -> Tuple[Vertical, List[PainInstance]]:
    """Create a vertical with three pains and return them."""
    vertical = Vertical(name="vertical-pains")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    signals = []
    for idx in range(3):
        signal = Signal(
            vertical_id=vertical.id,
            source="test",
            external_id=f"ext-{idx}",
            content=f"content {idx}",
        )
        db_session.add(signal)
        db_session.commit()
        db_session.refresh(signal)
        signals.append(signal)

    scores = [2.0, 3.0, 3.0]
    pains: List[PainInstance] = []
    for signal, score in zip(signals, scores):
        breakdown = {"score": score, "signal_id": signal.id}
        pain = PainInstance(
            vertical_id=vertical.id,
            signal_id=signal.id,
            algo_version="algo_v1",
            pain_score=score,
            breakdown=breakdown,
            breakdown_hash=breakdown_hash(breakdown),
        )
        db_session.add(pain)
        db_session.commit()
        db_session.refresh(pain)
        pains.append(pain)

    return vertical, pains


def test_pains_list_paginates_and_orders(client, db_session):
    """List endpoint should paginate and sort by score desc then id asc."""
    vertical, pains = _seed_pains(db_session)

    response = client.get(f"/pains?vertical_id={vertical.id}&limit=10&offset=0")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 3
    assert payload["page"] == {"limit": 10, "offset": 0}

    returned_ids = [item["id"] for item in payload["items"]]
    expected_ids = [p.id for p in sorted(pains, key=lambda p: (-p.pain_score, p.id))]
    assert returned_ids == expected_ids

    response_page = client.get(f"/pains?vertical_id={vertical.id}&limit=1&offset=1")
    assert response_page.status_code == 200

    payload_page = response_page.json()
    assert payload_page["total"] == 3
    assert payload_page["page"] == {"limit": 1, "offset": 1}
    assert [item["id"] for item in payload_page["items"]] == [expected_ids[1]]
