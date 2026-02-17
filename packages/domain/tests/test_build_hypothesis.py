from domain.insights.build_hypothesis import (
    compute_build_hypothesis,
    BuildHypothesisInputs,
)


def test_build_hypothesis_specific():
    h = compute_build_hypothesis(
        BuildHypothesisInputs(
            dominant_persona="Shopify founders",
            cluster_summary="Inventory mismatch after returns",
            key_phrases=["inventory mismatch"],
            exploitability_tier="STRONG_BUILD",
            breakout_score=5,
            contradiction_score=10,
        )
    )

    assert "inventory mismatch" in h.core_pain_statement.lower()
    assert h.target_persona == "Shopify founders"
