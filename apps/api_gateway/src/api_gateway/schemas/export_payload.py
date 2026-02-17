from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field, ConfigDict


class VentureOSExportPayloadV1Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_version: Literal["ventureos_export_v1"] = "ventureos_export_v1"
    hypothesis_id: str
    vertical_id: str
    taxonomy_version: str
    persona: str
    pain: str
    wedge: str
    monetization: Literal[
        "subscription",
        "usage-based",
        "per-seat",
        "premium add-on",
        "api-based",
        "one-off",
    ]
    validation_plan: List[str] = Field(min_length=3, max_length=3)
    opportunity_score: int
    timing_status: Literal["emerging", "stable", "declining", "breakout"]
    risks: List[str] = Field(default_factory=list)
