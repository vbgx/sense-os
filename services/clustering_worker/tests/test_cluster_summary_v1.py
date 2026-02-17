from __future__ import annotations

from clustering_worker.clustering.summary import SummaryInputs, synthesize_cluster_summary


def test_cluster_summary_is_stable_and_non_empty():
    inp = SummaryInputs(
        representative_texts=[
            "Shopify payout reconciliation mismatch after returns is killing us",
            "We keep getting mismatched CSV exports and refunds don't line up",
            "Any tool to fix reconciliation mismatch for returns on Shopify?",
        ],
        dominant_persona="founder",
        top_ngrams=None,
    )
    s1 = synthesize_cluster_summary(inp)
    s2 = synthesize_cluster_summary(inp)

    assert s1 == s2
    assert isinstance(s1, str)
    assert s1.strip() != ""
    assert "general" not in s1.lower()
    assert "frustration" not in s1.lower()


def test_cluster_summary_fallback_without_texts():
    inp = SummaryInputs(
        representative_texts=[],
        dominant_persona="operator",
        top_ngrams=["inventory mismatch", "csv export", "returns reconciliation"],
    )
    out = synthesize_cluster_summary(inp)
    assert out.strip() != ""
    assert "Operators" in out
