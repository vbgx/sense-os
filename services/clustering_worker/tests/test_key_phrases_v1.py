from __future__ import annotations

from clustering_worker.clustering.keyphrases import extract_key_phrases, KeyPhrasesInputs


def test_key_phrases_extracts_readable_phrases_and_no_trivial_dups():
    texts = [
        "CSV export is hell. CSV export hell after returns reconciliation mismatch.",
        "Inventory mismatch after returns, reconciliation mismatch, csv-export nightmare.",
        "Tax reporting nightmare: VAT returns reconciliation mismatch in CSV exports.",
    ]
    out = extract_key_phrases(KeyPhrasesInputs(texts=texts, top_k=10))
    assert out, "should extract phrases"
    # readable (no empty)
    assert all(p.strip() for p in out)
    # avoid trivial duplicates like "csv export" and "csv-export" both showing up
    norm = [p.lower().replace("-", " ").replace("_", " ").replace("/", " ") for p in out]
    assert len(set(norm)) == len(norm)


def test_key_phrases_filters_generic_spam():
    texts = [
        "Need help please anyone any advice general problem",
        "General frustration and issues, need help",
        "Any advice? anyone? help help help",
        "Real content: inventory mismatch after returns reconciliation",
    ]
    out = extract_key_phrases(KeyPhrasesInputs(texts=texts, top_k=10))
    assert out, "should still find something from real content"
    joined = " ".join(out).lower()
    assert "need help" not in joined
    assert "general" not in joined
    assert "frustration" not in joined
