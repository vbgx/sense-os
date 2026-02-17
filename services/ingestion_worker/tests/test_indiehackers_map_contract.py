from ingestion_worker.adapters.indiehackers.map import map_indiehackers_entry


def test_map_indiehackers_entry_contract():
    entry = {
        "guid": "abc123",
        "title": "How I reached $10k MRR",
        "summary": "Struggling with churn and pricing.",
        "link": "https://example.com",
    }

    d = map_indiehackers_entry(
        entry,
        vertical_id="b2b_ops",
        vertical_db_id=1,
        taxonomy_version="2026-02-17",
    )

    assert set(d.keys()) == {
        "vertical_id",
        "vertical_db_id",
        "taxonomy_version",
        "source",
        "external_id",
        "content",
        "url",
        "language",
    }
    assert d["source"] == "indiehackers"
    assert d["external_id"].startswith("ih:")
    assert d["content"]
