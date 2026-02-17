from domain.insights.target_persona_v1 import generate_target_persona


class DummyCluster:
    def __init__(self, dominant_persona, key_phrases, representative_signals):
        self.dominant_persona = dominant_persona
        self.key_phrases = key_phrases
        self.representative_signals = representative_signals


def test_generate_target_persona_shopify_early_returns():
    cluster = DummyCluster(
        dominant_persona="founder",
        key_phrases=["Shopify store", "returns", "refund policy"],
        representative_signals=["We just launched", "too many returns"]
    )

    result = generate_target_persona(cluster)

    assert "Shopify" in result.primary_persona
    assert "founders" in result.primary_persona
    assert "returns-heavy" in result.primary_persona
    assert result.confidence_score >= 0.8


def test_generate_target_persona_scaling_saas():
    cluster = DummyCluster(
        dominant_persona="founder",
        key_phrases=["SaaS churn problem"],
        representative_signals=["scaling fast", "high churn rates"]
    )

    result = generate_target_persona(cluster)

    assert "Scaling" in result.primary_persona
    assert "SaaS" in result.primary_persona
    assert "high-churn" in result.primary_persona


def test_generate_target_persona_no_generic_business_owner():
    cluster = DummyCluster(
        dominant_persona="founder",
        key_phrases=["inventory issues"],
        representative_signals=["operational friction"]
    )

    result = generate_target_persona(cluster)

    assert "business owner" not in result.primary_persona.lower()
    assert "founders" in result.primary_persona


def test_generate_target_persona_stable_output():
    cluster = DummyCluster(
        dominant_persona="operator",
        key_phrases=["support overload"],
        representative_signals=["too many tickets"]
    )

    result1 = generate_target_persona(cluster)
    result2 = generate_target_persona(cluster)

    assert result1.primary_persona == result2.primary_persona
    assert result1.confidence_score == result2.confidence_score
