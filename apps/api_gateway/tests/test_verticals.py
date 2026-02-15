from db.repos import verticals as vertical_repo


def test_verticals_list(client, db_session):
    vertical_repo.create(db_session, "alpha")
    vertical_repo.create(db_session, "beta")

    resp = client.get("/verticals")
    assert resp.status_code == 200
    data = resp.json()
    names = {v["name"] for v in data}
    assert {"alpha", "beta"}.issubset(names)
