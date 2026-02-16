from fastapi.testclient import TestClient
from api_gateway.main import app

client = TestClient(app)


def test_top_pains_endpoint_exists():
    resp = client.get("/insights/top_pains")
    assert resp.status_code in (200, 204)


def test_top_pains_sorted_desc():
    resp = client.get("/insights/top_pains?limit=5")
    assert resp.status_code == 200
    data = resp.json()

    if len(data) >= 2:
        assert data[0]["exploitability_score"] >= data[1]["exploitability_score"]
