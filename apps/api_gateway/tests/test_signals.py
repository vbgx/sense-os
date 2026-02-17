from db.models import Signal, Vertical


def test_signals_list(client, db_session):
    vertical = Vertical(name="alpha")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    sig = Signal(
        vertical_db_id=vertical.id,
        vertical_id=vertical.name,
        source="reddit",
        external_id="ext-1",
        content="example",
    )
    db_session.add(sig)
    db_session.commit()

    resp = client.get(f"/signals?vertical_id={vertical.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["external_id"] == "ext-1"
