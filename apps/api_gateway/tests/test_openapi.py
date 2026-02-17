def test_openapi_served(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "/insights/{cluster_id}/export" in data.get("paths", {})
