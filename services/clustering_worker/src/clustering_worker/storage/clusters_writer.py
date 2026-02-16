from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Optional

from clustering_worker.storage.severity import InstanceForSeverity, compute_cluster_severity
from clustering_worker.storage.recurrence import InstanceForRecurrence, compute_cluster_recurrence


@dataclass(frozen=True)
class ClusterWriteModel:
    """
    Minimal write-model expected by the DB layer.
    """
    cluster_id: str
    vertical_id: str
    title: str
    size: int
    severity_score: int
    recurrence_score: int
    recurrence_ratio: float


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
    # best-effort ISO parse
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
    """
    Builds a cluster payload for persistence, including:
      - Pain Severity Index (severity_score)
      - Recurrence Detection (recurrence_score + recurrence_ratio)

    instance_rows: dicts should (best-effort) include:
      - text
      - sentiment_compound (or sentiment)
      - upvotes/comments/replies
      - user_id (or author_id / user)
      - source_id (post id)
      - created_at (datetime or ISO)
    """
    rows = list(instance_rows)

    # Severity adapter
    sev_instances = []
    for r in rows:
        sev_instances.append(
            InstanceForSeverity(
                text=str(r.get("text") or r.get("body") or ""),
                sentiment_compound=_to_float_or_none(r.get("sentiment_compound", r.get("sentiment"))),
                upvotes=_to_int(r.get("upvotes", r.get("score", 0))),
                comments=_to_int(r.get("comments", r.get("num_comments", 0))),
                replies=_to_int(r.get("replies", 0)),
            )
        )

    severity = compute_cluster_severity(sev_instances)

    # Recurrence adapter
    rec_instances = []
    for r in rows:
        rec_instances.append(
            InstanceForRecurrence(
                text=str(r.get("text") or r.get("body") or ""),
                user_id=(r.get("user_id") or r.get("author_id") or r.get("author") or r.get("user")),
                source_id=(r.get("source_id") or r.get("id")),
                created_at=_to_dt_or_none(r.get("created_at")),
            )
        )

    recurrence_score, recurrence_ratio = compute_cluster_recurrence(rec_instances)

    return ClusterWriteModel(
        cluster_id=cluster_id,
        vertical_id=vertical_id,
        title=title,
        size=len(rows),
        severity_score=severity,
        recurrence_score=recurrence_score,
        recurrence_ratio=float(recurrence_ratio),
    )
