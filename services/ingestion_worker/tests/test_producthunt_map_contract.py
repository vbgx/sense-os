from ingestion_worker.adapters.producthunt.map import map_producthunt_entry


def test_map_producthunt_entry_contract():
    entry = {
        "guid": "xyz123",
        "title": "New AI Tool",
        "summary": "<p>Helps founders automate churn reduction</p>",
        "link": "https://example.com",
    }

    d = map_producthunt_entry(
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
    }
    assert d["source"] == "producthunt"
    assert d["external_id"].startswith("ph:")
    assert d["content"]
