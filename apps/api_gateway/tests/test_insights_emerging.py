from fastapi.testclient import TestClient
from api_gateway.main import app

client = TestClient(app)


def test_emerging_endpoint_exists():
    resp = client.get("/insights/emerging_opportunities")
    assert resp.status_code in (200, 204)


def test_emerging_filter_logic():
    resp = client.get("/insights/emerging_opportunities?limit=10")
    assert resp.status_code == 200
    data = resp.json()

    for item in data:
        assert item["opportunity_window_status"] == "EARLY"
