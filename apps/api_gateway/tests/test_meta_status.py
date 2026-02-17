from __future__ import annotations


def test_meta_status_returns_expected_shape(client):
    r = client.get("/meta/status")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, dict)

    assert "last_run_at" in data
    assert "scoring_version" in data
    assert "total_signals_7d" in data
    assert "total_clusters" in data

    assert data["last_run_at"] is None or isinstance(data["last_run_at"], str)
    assert isinstance(data["scoring_version"], str)
    assert isinstance(data["total_signals_7d"], int)
    assert isinstance(data["total_clusters"], int)
