from api_gateway.schemas.export_payload import VentureOSExportPayloadV1Schema


def test_valid_export_payload_contract():
    payload = {
        "export_version": "ventureos_export_v1",
        "hypothesis_id": "hyp_123_abcdefabcdefabcd",
        "persona": "Early-stage Shopify founders",
        "pain": "Early-stage Shopify founders struggle with persistent return reconciliation because manual processes",
        "wedge": "Automated reconciliation layer for Early-stage Shopify founders",
        "monetization": "subscription",
        "validation_plan": ["step1", "step2", "step3"],
        "opportunity_score": 80,
        "timing_status": "emerging",
        "risks": ["High competition density"],
    }

    model = VentureOSExportPayloadV1Schema.model_validate(payload)
    assert model.export_version == "ventureos_export_v1"
    assert len(model.validation_plan) == 3


def test_extra_field_forbidden():
    payload = {
        "export_version": "ventureos_export_v1",
        "hypothesis_id": "hyp_123",
        "persona": "SaaS founders",
        "pain": "SaaS founders struggle with churn because manual processes",
        "wedge": "Workflow simplification layer",
        "monetization": "subscription",
        "validation_plan": ["a", "b", "c"],
        "opportunity_score": 10,
        "timing_status": "stable",
        "risks": [],
        "unexpected": "field",
    }

    try:
        VentureOSExportPayloadV1Schema.model_validate(payload)
        raise AssertionError("Expected validation error")
    except Exception:
        pass

