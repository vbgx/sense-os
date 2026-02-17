from domain.insights.monetization_angle_v1 import generate_monetization_angle


class DummyCluster:
    def __init__(self, summary, key_phrases, monetizability_score):
        self.cluster_summary = summary
        self.key_phrases = key_phrases
        self.monetizability_score = monetizability_score


def test_high_score_subscription():
    cluster = DummyCluster(
        summary="Recurring refund reconciliation issues",
        key_phrases=["manual reconciliation"],
        monetizability_score=5
    )

    result = generate_monetization_angle(cluster, "Shopify founders")

    assert result.model in ["subscription", "api-based", "per-seat", "usage-based"]
    assert result.pricing_power_estimate == "high"


def test_team_context_per_seat():
    cluster = DummyCluster(
        summary="Team workflow coordination friction",
        key_phrases=["operators involved"],
        monetizability_score=4
    )

    result = generate_monetization_angle(cluster, "Operations team operators")

    assert result.pricing_power_estimate == "high"


def test_low_score_one_off():
    cluster = DummyCluster(
        summary="Occasional reporting inconvenience",
        key_phrases=["minor reporting"],
        monetizability_score=1
    )

    result = generate_monetization_angle(cluster, "Freelancers")

    assert result.model == "one-off"
    assert result.pricing_power_estimate == "low"
