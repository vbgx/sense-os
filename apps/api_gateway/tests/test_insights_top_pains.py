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

def test_top_pains_includes_vertical_and_saturation(client):
    r = client.get("/insights/top_pains?limit=1&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if not data:
        return
    item = data[0]
    assert "vertical_id" in item
    assert "saturation_score" in item
    assert isinstance(item["saturation_score"], int)
