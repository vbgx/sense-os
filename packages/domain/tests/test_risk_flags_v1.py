from domain.insights.risk_flags_v1 import generate_risk_flags


class DummyCluster:
    def __init__(
        self,
        contradiction_score=0,
        competitive_heat_score=0,
        saturation_score=0,
        confidence_score=1.0,
    ):
        self.contradiction_score = contradiction_score
        self.competitive_heat_score = competitive_heat_score
        self.saturation_score = saturation_score
        self.confidence_score = confidence_score


def test_high_competition_flag():
    cluster = DummyCluster(competitive_heat_score=5)
    flags = generate_risk_flags(cluster)
    assert "High competition density" in flags


def test_saturation_flag():
    cluster = DummyCluster(saturation_score=4)
    flags = generate_risk_flags(cluster)
    assert "Trend showing early saturation" in flags


def test_low_confidence_flag():
    cluster = DummyCluster(confidence_score=0.3)
    flags = generate_risk_flags(cluster)
    assert "Low cluster confidence" in flags


def test_multiple_flags():
    cluster = DummyCluster(
        contradiction_score=5,
        competitive_heat_score=5,
        saturation_score=5,
        confidence_score=0.2,
    )
    flags = generate_risk_flags(cluster)
    assert len(flags) == 4
