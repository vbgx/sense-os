from domain.insights.suggested_wedge_v1 import generate_suggested_wedge


class DummyCluster:
    def __init__(self, summary, key_phrases):
        self.cluster_summary = summary
        self.key_phrases = key_phrases


def test_automation_wedge_generation():
    cluster = DummyCluster(
        summary="Handling returns is manual and time consuming",
        key_phrases=["refund reconciliation", "manual tracking"]
    )

    result = generate_suggested_wedge(
        cluster,
        "Shopify founders managing return-heavy stores",
        "Shopify founders struggle with return reconciliation because workflows are fragmented"
    )

    assert result.wedge_type == "automation"
    assert "Shopify founders" in result.description


def test_aggregation_wedge_generation():
    cluster = DummyCluster(
        summary="Data is scattered across multiple tools",
        key_phrases=["spreadsheet chaos"]
    )

    result = generate_suggested_wedge(
        cluster,
        "SaaS operators",
        "SaaS operators struggle with scattered data because processes are fragmented"
    )

    assert result.wedge_type == "aggregation"


def test_wedge_not_generic():
    cluster = DummyCluster(
        summary="Workflow approvals are slow",
        key_phrases=["approval process"]
    )

    result = generate_suggested_wedge(
        cluster,
        "Agency owners",
        "Agency owners struggle with slow approvals because coordination is unclear"
    )

    assert "Build SaaS" not in result.description
    assert "Agency owners" in result.description
