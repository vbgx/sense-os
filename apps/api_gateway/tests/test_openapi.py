def test_openapi_served(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    paths = data.get("paths", {})

    # existing critical endpoints
    assert "/insights/{cluster_id}/export" in paths
    assert "/verticals/{vertical_id}/ventureos_export" in paths

    # new overview endpoint
    assert "/overview" in paths

    # basic schema presence for /overview GET 200
    overview_get = paths["/overview"].get("get", {})
    responses = overview_get.get("responses", {})
    assert "200" in responses

    content = responses["200"].get("content", {})
    assert "application/json" in content
    assert content["application/json"].get("schema"), "Missing response schema for /overview"
