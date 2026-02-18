from domain.models.daily_metric import DailyMetric


def test_clustering_to_trend_daily_metric_contract():
    payload = {
        "vertical_db_id": 1,
        "taxonomy_version": "v1",
        "cluster_id": 10,
        "day": "2026-02-18",
        "count": 5,
    }
    DailyMetric.model_validate(payload)
