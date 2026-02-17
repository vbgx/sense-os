def test_verticals_list_includes_vic_fields(client):
    resp = client.get("/verticals")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["items"]

    sample = data["items"][0]
    assert "meta" in sample
    assert "tier" in sample
    assert "taxonomy_version" in sample
    assert isinstance(sample["taxonomy_version"], str)
