from fastapi.testclient import TestClient
from api_gateway.main import app

client = TestClient(app)


def test_declining_endpoint_exists():
    resp = client.get("/insights/declining_risks")
    assert resp.status_code in (200, 204)


def test_declining_filter_logic():
    resp = client.get("/insights/declining_risks?limit=10")
    assert resp.status_code == 200
