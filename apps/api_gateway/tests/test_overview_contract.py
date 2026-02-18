from fastapi.testclient import TestClient
from api_gateway.main import app
from api_gateway.schemas.overview import OverviewOut


def _validate(payload: dict) -> None:
    if hasattr(OverviewOut, "model_validate"):
        OverviewOut.model_validate(payload)  # pydantic v2
    else:
        OverviewOut.parse_obj(payload)  # pydantic v1


def test_overview_contract():
    c = TestClient(app)
    r = c.get("/overview")
    assert r.status_code == 200, r.text

    data = r.json()
    _validate(data)

    assert len(data["kpis"]) == 5
    keys = {k["key"] for k in data["kpis"]}
    assert keys == {
        "total_active_verticals",
        "emerging_clusters_7d",
        "declining_clusters",
        "opportunity_volatility_index",
        "signal_growth_7d",
    }

    # breakouts shape
    for row in data["breakouts"]:
        assert isinstance(row["rank"], int)
        assert isinstance(row["score"], (int, float))
        assert isinstance(row["momentum_7d"], (int, float))
        assert 0.0 <= float(row["confidence"]) <= 1.0
