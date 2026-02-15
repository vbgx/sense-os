from db.models import PainCluster, Vertical


def test_clusters_list(client, db_session):
    vertical = Vertical(name="alpha")
    db_session.add(vertical)
    db_session.commit()
    db_session.refresh(vertical)

    cluster = PainCluster(
        vertical_id=vertical.id,
        cluster_version="tfidf_v1",
        cluster_key="k1",
        title="billing pain",
        size=12,
    )
    db_session.add(cluster)
    db_session.commit()

    resp = client.get(f"/clusters?vertical_id={vertical.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "billing pain"
