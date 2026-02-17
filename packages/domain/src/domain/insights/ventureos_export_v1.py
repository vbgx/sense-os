from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List, Optional


EXPORT_VERSION = "ventureos_export_v1"
ALLOWED_MONETIZATION_MODELS = (
    "subscription",
    "usage-based",
    "per-seat",
    "premium add-on",
    "api-based",
    "one-off",
)
ALLOWED_TIMING_STATUS = (
    "emerging",
    "stable",
    "declining",
    "breakout",
)


@dataclass(frozen=True)
class VentureOSExportPayloadV1:
    export_version: str
    hypothesis_id: str
    vertical_id: str
    taxonomy_version: str
    persona: str
    pain: str
    wedge: str
    monetization: str
    validation_plan: List[str]
    opportunity_score: int
    timing_status: str
    risks: List[str]


def _stable_hypothesis_id(cluster_id: str) -> str:
    raw = f"{EXPORT_VERSION}:{cluster_id}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:16]
    return f"hyp_{cluster_id}_{digest}"


def build_ventureos_export_payload_v1(
    *,
    cluster_id: str,
    vertical_id: str,
    taxonomy_version: str,
    persona: str,
    pain: str,
    wedge: str,
    monetization: str,
    validation_plan: List[str],
    opportunity_score: int,
    timing_status: str,
    risks: Optional[List[str]] = None,
) -> VentureOSExportPayloadV1:

    if not cluster_id:
        raise ValueError("cluster_id is required")

    if not persona or "business owner" in persona.lower():
        raise ValueError("persona must be specific and non-generic")

    if not pain or "struggle with" not in pain or "because" not in pain:
        raise ValueError("pain must follow structured format")

    if not wedge or "build saas" in wedge.lower():
        raise ValueError("wedge must be specific and non-generic")

    if monetization not in ALLOWED_MONETIZATION_MODELS:
        raise ValueError("monetization must be a supported model string")

    if (
        not isinstance(validation_plan, list)
        or len(validation_plan) != 3
        or not all(isinstance(step, str) and step.strip() for step in validation_plan)
    ):
        raise ValueError("validation_plan must contain exactly 3 non-empty steps")

    if not isinstance(opportunity_score, int):
        raise ValueError("opportunity_score must be an integer")

    if timing_status not in ALLOWED_TIMING_STATUS:
        raise ValueError("timing_status must be emerging|stable|declining|breakout")

    payload = VentureOSExportPayloadV1(
        export_version=EXPORT_VERSION,
        hypothesis_id=_stable_hypothesis_id(cluster_id),
        vertical_id=str(vertical_id).strip(),
        taxonomy_version=str(taxonomy_version).strip(),
        persona=persona.strip(),
        pain=pain.strip(),
        wedge=wedge.strip(),
        monetization=monetization,
        validation_plan=[step.strip() for step in validation_plan],
        opportunity_score=opportunity_score,
        timing_status=timing_status,
        risks=[r.strip() for r in (risks or []) if isinstance(r, str) and r.strip()],
    )

    return payload


def to_dict(payload: VentureOSExportPayloadV1) -> dict:
    return {
        "export_version": payload.export_version,
        "hypothesis_id": payload.hypothesis_id,
        "vertical_id": payload.vertical_id,
        "taxonomy_version": payload.taxonomy_version,
        "persona": payload.persona,
        "pain": payload.pain,
        "wedge": payload.wedge,
        "monetization": payload.monetization,
        "validation_plan": payload.validation_plan,
        "opportunity_score": payload.opportunity_score,
        "timing_status": payload.timing_status,
        "risks": payload.risks,
    }
