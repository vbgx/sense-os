from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Optional

from clustering_worker.storage.severity import InstanceForSeverity, compute_cluster_severity
from clustering_worker.storage.recurrence import InstanceForRecurrence, compute_cluster_recurrence
from clustering_worker.storage.persona import InstanceForPersona, infer_cluster_persona_from_instances
from clustering_worker.storage.monetizability import InstanceForMonetizability, compute_cluster_monetizability
from clustering_worker.storage.contradiction import InstanceForContradiction, compute_cluster_contradiction


@dataclass(frozen=True)
class ClusterWriteModel:
    cluster_id: str
    vertical_id: str
    title: str
    size: int
    severity_score: int
    recurrence_score: int
    recurrence_ratio: float
    dominant_persona: str
    persona_confidence: float
    persona_distribution: dict[str, float]
    monetizability_score: int
    contradiction_score: int


def _to_int(x: Any) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def _to_float_or_none(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def _to_dt_or_none(x: Any) -> Optional[datetime]:
    if x is None:
        return None
    if isinstance(x, datetime):
        return x
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except Exception:
        return None


def build_cluster_write_model(
    *,
    cluster_id: str,
    vertical_id: str,
    title: str,
    instance_rows: Iterable[dict[str, Any]],
) -> ClusterWriteModel:
    rows = list(instance_rows)

    # Severity
    sev_instances = [
        InstanceForSeverity(
            text=str(r.get("text") or r.get("body") or ""),
            sentiment_compound=_to_float_or_none(r.get("sentiment_compound", r.get("sentiment"))),
            upvotes=_to_int(r.get("upvotes", r.get("score", 0))),
            comments=_to_int(r.get("comments", r.get("num_comments", 0))),
            replies=_to_int(r.get("replies", 0)),
        )
        for r in rows
    ]
    severity = compute_cluster_severity(sev_instances)

    # Recurrence
    rec_instances = [
        InstanceForRecurrence(
            text=str(r.get("text") or r.get("body") or ""),
            user_id=(r.get("user_id") or r.get("author_id") or r.get("author") or r.get("user")),
            source_id=(r.get("source_id") or r.get("id")),
            created_at=_to_dt_or_none(r.get("created_at")),
        )
        for r in rows
    ]
    recurrence_score, recurrence_ratio = compute_cluster_recurrence(rec_instances)

    # Persona
    persona_instances = [InstanceForPersona(text=str(r.get("text") or r.get("body") or "")) for r in rows]
    persona_inf = infer_cluster_persona_from_instances(persona_instances)

    dominant_persona = str(persona_inf.dominant_persona.value)
    persona_confidence = float(persona_inf.confidence)
    persona_distribution = {str(k.value): float(v) for k, v in persona_inf.distribution.items()}

    # Monetizability (persona-weighted)
    mon_instances = [
        InstanceForMonetizability(
            text=str(r.get("text") or r.get("body") or ""),
            persona=dominant_persona,
        )
        for r in rows
    ]
    monetizability_score = compute_cluster_monetizability(mon_instances)

    # Contradiction
    con_instances = [
        InstanceForContradiction(
            sentiment_compound=_to_float_or_none(r.get("sentiment_compound", r.get("sentiment"))),
            created_at=_to_dt_or_none(r.get("created_at")),
        )
        for r in rows
    ]
    contradiction_score = compute_cluster_contradiction(con_instances)

    return ClusterWriteModel(
        cluster_id=cluster_id,
        vertical_id=vertical_id,
        title=title,
        size=len(rows),
        severity_score=severity,
        recurrence_score=recurrence_score,
        recurrence_ratio=float(recurrence_ratio),
        dominant_persona=dominant_persona,
        persona_confidence=persona_confidence,
        persona_distribution=persona_distribution,
        monetizability_score=monetizability_score,
        contradiction_score=contradiction_score,
    )
