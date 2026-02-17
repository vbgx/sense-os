import pytest
from pydantic import ValidationError

from api_gateway.schemas.export_payload import VentureOSExportPayloadV1Schema
from domain.insights.ventureos_export_v1 import (
    build_ventureos_export_payload_v1,
    to_dict,
)


def _valid_payload() -> dict:
    payload = build_ventureos_export_payload_v1(
        cluster_id="cluster-123",
        vertical_id="industry_retail",
        taxonomy_version="2026-02-17",
        persona="Early-stage Shopify founders",
        pain="Early-stage Shopify founders struggle with persistent return reconciliation because manual processes",
        wedge="Automated reconciliation layer for Early-stage Shopify founders",
        monetization="subscription",
        validation_plan=["step1", "step2", "step3"],
        opportunity_score=80,
        timing_status="emerging",
        risks=["High competition density"],
    )
    return to_dict(payload)


def test_valid_export_payload_contract():
    payload = _valid_payload()
    model = VentureOSExportPayloadV1Schema.model_validate(payload)
    assert model.export_version == "ventureos_export_v1"
    assert len(model.validation_plan) == 3


def test_invalid_monetization_fails():
    payload = _valid_payload()
    payload["monetization"] = "ads"

    with pytest.raises(ValidationError):
        VentureOSExportPayloadV1Schema.model_validate(payload)


def test_invalid_validation_plan_length_fails():
    payload = _valid_payload()
    payload["validation_plan"] = payload["validation_plan"][:2]

    with pytest.raises(ValidationError):
        VentureOSExportPayloadV1Schema.model_validate(payload)


def test_extra_field_forbidden():
    payload = _valid_payload()
    payload["unexpected"] = "field"

    with pytest.raises(ValidationError):
        VentureOSExportPayloadV1Schema.model_validate(payload)
