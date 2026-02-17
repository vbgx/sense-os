from domain.insights.core_pain_statement_v1 import generate_core_pain_statement


class DummyCluster:
    def __init__(self, summary, severity_score, key_phrases):
        self.cluster_summary = summary
        self.severity_score = severity_score
        self.key_phrases = key_phrases


def test_generate_pain_statement_with_root_cause():
    cluster = DummyCluster(
        summary="Handling returns is chaotic because refund policies are unclear",
        severity_score=4,
        key_phrases=["returns", "refund policy"]
    )

    statement = generate_core_pain_statement(cluster, "Shopify founders")

    assert "Shopify founders" in statement
    assert "struggle with" in statement
    assert "because" in statement
    assert "refund policies are unclear" in statement


def test_generate_pain_statement_without_explicit_cause():
    cluster = DummyCluster(
        summary="Inventory tracking is inconsistent",
        severity_score=3,
        key_phrases=["inventory tracking"]
    )

    statement = generate_core_pain_statement(cluster, "SaaS operators")

    assert "persistent" in statement
    assert "because" in statement


def test_generate_pain_statement_stable():
    cluster = DummyCluster(
        summary="Customer support overload",
        severity_score=2,
        key_phrases=["support overload"]
    )

    s1 = generate_core_pain_statement(cluster, "Agency owners")
    s2 = generate_core_pain_statement(cluster, "Agency owners")

    assert s1 == s2
