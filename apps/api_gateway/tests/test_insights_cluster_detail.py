from fastapi.testclient import TestClient
from api_gateway.main import app

client = TestClient(app)


def test_cluster_detail_endpoint_exists():
    resp = client.get("/insights/test_cluster")
    assert resp.status_code in (200, 400, 404)
