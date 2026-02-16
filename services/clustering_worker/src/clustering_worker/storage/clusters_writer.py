from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

from clustering_worker.storage.severity import InstanceForSeverity, compute_cluster_severity


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


def build_cluster_write_model(
    *,
    cluster_id: str,
    vertical_id: str,
    title: str,
    instance_rows: Iterable[dict[str, Any]],
) -> ClusterWriteModel:
    """
    Builds a cluster payload for persistence, including the Pain Severity Index.

    instance_rows: dicts should (best-effort) include:
      - text
      - sentiment_compound (or sentiment)
      - upvotes
      - comments
      - replies
    """
    rows = list(instance_rows)

    instances = []
    for r in rows:
        instances.append(
            InstanceForSeverity(
                text=str(r.get("text") or r.get("body") or ""),
                sentiment_compound=_to_float_or_none(r.get("sentiment_compound", r.get("sentiment"))),
                upvotes=_to_int(r.get("upvotes", r.get("score", 0))),
                comments=_to_int(r.get("comments", r.get("num_comments", 0))),
                replies=_to_int(r.get("replies", 0)),
            )
        )

    severity = compute_cluster_severity(instances)

    return ClusterWriteModel(
        cluster_id=cluster_id,
        vertical_id=vertical_id,
        title=title,
        size=len(rows),
        severity_score=severity,
    )
