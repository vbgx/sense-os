from ingestion_worker.adapters.indiehackers.map import map_indiehackers_entry


def test_map_indiehackers_entry_contract():
    entry = {
        "guid": "abc123",
        "title": "How I reached $10k MRR",
        "summary": "Struggling with churn and pricing.",
        "link": "https://example.com",
    }

    d = map_indiehackers_entry(entry, vertical_id=5)

    assert set(d.keys()) == {"vertical_id", "source", "external_id", "content", "url", "language"}
    assert d["source"] == "indiehackers"
    assert d["external_id"].startswith("ih:")
    assert d["content"]
