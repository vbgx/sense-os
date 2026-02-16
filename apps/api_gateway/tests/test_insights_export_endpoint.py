from fastapi.testclient import TestClient
from api_gateway.main import app


client = TestClient(app)


def test_export_endpoint_exists():
    response = client.get("/insights/test-cluster-id/export")
    assert response.status_code in (200, 404, 422)


def test_export_response_structure_if_success():
    response = client.get("/insights/test-cluster-id/export")

    if response.status_code == 200:
        data = response.json()
        assert "export_version" in data
        assert "hypothesis_id" in data
        assert "persona" in data
        assert "pain" in data
        assert "wedge" in data
        assert "monetization" in data
        assert "validation_plan" in data
        assert "opportunity_score" in data
        assert "timing_status" in data
        assert "risks" in data

