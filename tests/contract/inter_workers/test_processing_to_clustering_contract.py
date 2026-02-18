from domain.models.pain_instance import PainInstance
from domain.models.pain_cluster import PainCluster


def test_processing_to_clustering_payloads_contract():
    instance_payload = {
        "id": 1,
        "signal_id": 123,
        "vertical_db_id": 1,
        "taxonomy_version": "v1",
        "text": "Autovacuum is too slow on large tables",
        "pain_score": 0.71,
    }
    PainInstance.model_validate(instance_payload)

    cluster_payload = {
        "id": 10,
        "vertical_db_id": 1,
        "taxonomy_version": "v1",
        "title": "Autovacuum tuning pain",
        "summary": "Users struggle with vacuum and bloat under write-heavy workloads",
        "representative_signal_ids": [123, 456],
        "severity_score": 0.7,
        "recurrence_score": 0.6,
        "monetizability_score": 0.4,
        "contradiction_score": 0.1,
        "competitive_heat_score": 0.3,
        "confidence_score": 0.8,
    }
    PainCluster.model_validate(cluster_payload)
