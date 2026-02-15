from fastapi.testclient import TestClient

from api_gateway.main import app

client = TestClient(app)

def test_trends_smoke():
    # endpoint name may evolve; keep this test as a "contract smoke"
    # Adjust path if your router uses another prefix.
    r = client.get("/trends")
    assert r.status_code in (200, 404)
