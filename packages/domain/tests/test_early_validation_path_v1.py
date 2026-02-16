from domain.insights.early_validation_path_v1 import generate_early_validation_path


class DummyCluster:
    def __init__(self, summary, key_phrases, representative_signals):
        self.cluster_summary = summary
        self.key_phrases = key_phrases
        self.representative_signals = representative_signals


def test_validation_path_contains_three_steps():
    cluster = DummyCluster(
        summary="Return reconciliation issues discussed on Reddit",
        key_phrases=["shopify returns"],
        representative_signals=["Reddit discussion about refund chaos"]
    )

    result = generate_early_validation_path(cluster, "Shopify founders")

    assert len(result.steps) == 3


def test_validation_path_is_persona_specific():
    cluster = DummyCluster(
        summary="Workflow friction",
        key_phrases=["manual processing"],
        representative_signals=[]
    )

    result = generate_early_validation_path(cluster, "Agency owners")

    for step in result.steps:
        assert "Agency owners" in step


def test_validation_path_reddit_specific():
    cluster = DummyCluster(
        summary="Pain heavily discussed on Reddit",
        key_phrases=[],
        representative_signals=["reddit thread"]
    )

    result = generate_early_validation_path(cluster, "SaaS founders")

    assert any("subreddit" in step.lower() for step in result.steps)
