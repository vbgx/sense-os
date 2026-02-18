from domain.verticals.contract_v1 import RawSignalV1
from domain.models.pain_instance import PainInstance


def test_ingestion_payload_is_rawsignal_v1_contract():
    payload = {
        "vertical_db_id": 1,
        "taxonomy_version": "v1",
        "source": "hackernews",
        "source_external_id": "hn:123",
        "title": "Postgres vacuum not keeping up",
        "text": "Autovacuum is too slow on large tables",
        "url": "https://example.com/x",
        "created_at": "2026-02-18T00:00:00Z",
        "author": "user",
        "score": 10,
    }
    RawSignalV1.model_validate(payload)


def test_processing_output_is_paininstance_contract():
    payload = {
        "signal_id": 123,
        "vertical_db_id": 1,
        "taxonomy_version": "v1",
        "pain_score": 0.71,
    }
    PainInstance.model_validate(payload)
