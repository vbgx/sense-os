from dataclasses import dataclass
from typing import List


@dataclass
class SuggestedWedgeResult:
    wedge_type: str
    description: str


_AUTOMATION_KEYWORDS = [
    "manual", "reconcile", "reconciliation", "processing", "handling",
    "tracking", "updating", "refund", "return"
]

_AGGREGATION_KEYWORDS = [
    "multiple tools", "spreadsheet", "spreadsheet", "data scattered",
    "different platforms", "fragmented"
]

_WORKFLOW_KEYWORDS = [
    "workflow", "process", "approval", "handoff", "coordination"
]

_ALERTING_KEYWORDS = [
    "missed", "late", "delay", "unexpected", "failure"
]

_REPORTING_KEYWORDS = [
    "visibility", "reporting", "insight", "analytics", "dashboard"
]


def _contains_any(text: str, keywords: List[str]) -> bool:
    text = text.lower()
    return any(k in text for k in keywords)


def generate_suggested_wedge(cluster, target_persona: str, core_pain_statement: str) -> SuggestedWedgeResult:
    text = (cluster.cluster_summary or "") + " " + " ".join(cluster.key_phrases or [])
    text = text.lower()

    persona_clean = target_persona.strip()

    if _contains_any(text, _AUTOMATION_KEYWORDS):
        wedge_type = "automation"
        description = f"Automated reconciliation and execution layer for {persona_clean}"
    elif _contains_any(text, _AGGREGATION_KEYWORDS):
        wedge_type = "aggregation"
        description = f"Centralized aggregation dashboard tailored for {persona_clean}"
    elif _contains_any(text, _WORKFLOW_KEYWORDS):
        wedge_type = "workflow"
        description = f"Simplified workflow orchestration layer for {persona_clean}"
    elif _contains_any(text, _ALERTING_KEYWORDS):
        wedge_type = "alerting"
        description = f"Proactive alerting system designed for {persona_clean}"
    elif _contains_any(text, _REPORTING_KEYWORDS):
        wedge_type = "reporting"
        description = f"Focused reporting interface built for {persona_clean}"
    else:
        wedge_type = "automation"
        description = f"Targeted automation layer addressing core friction for {persona_clean}"

    return SuggestedWedgeResult(
        wedge_type=wedge_type,
        description=description
    )

