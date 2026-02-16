from ingestion_worker.adapters.producthunt.map import map_producthunt_entry


def test_map_producthunt_entry_contract():
    entry = {
        "guid": "xyz123",
        "title": "New AI Tool",
        "summary": "<p>Helps founders automate churn reduction</p>",
        "link": "https://example.com",
    }

    d = map_producthunt_entry(entry, vertical_id=9)

    assert set(d.keys()) == {"vertical_id", "source", "external_id", "content", "url"}
    assert d["source"] == "producthunt"
    assert d["external_id"].startswith("ph:")
    assert d["content"]
