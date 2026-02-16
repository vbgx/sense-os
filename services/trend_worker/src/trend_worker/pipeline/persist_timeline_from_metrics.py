from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from trend_worker.timeline import DailyVolume, compute_timeline
from trend_worker.storage.cluster_daily_history import persist_cluster_daily_history


@dataclass(frozen=True)
class MetricRow:
    day: date
    frequency: int


def _load_daily_frequencies(
    db: Session,
    *,
    cluster_id: int,
    formula_version: str,
    days: int,
) -> List[MetricRow]:
    # Uses the same source-of-truth as trend metrics persistence.
    # NOTE: assumes table name "cluster_daily_metrics" with columns: cluster_id, day, formula_version, frequency
    stmt = text(
        """
        SELECT day, frequency
        FROM cluster_daily_metrics
        WHERE cluster_id = :cluster_id
          AND formula_version = :formula_version
        ORDER BY day ASC
        """
    )
    rows = db.execute(stmt, {"cluster_id": cluster_id, "formula_version": formula_version}).all()

    if days and len(rows) > days:
        rows = rows[-days:]

    out: List[MetricRow] = []
    for r in rows:
        out.append(MetricRow(day=r[0], frequency=int(r[1])))
    return out


def persist_timeline_from_trend_metrics(
    db: Session,
    *,
    cluster_id: int,
    formula_version: str,
    days: int = 90,
) -> None:
    """
    Build and persist timeline points from existing trend metrics (frequency per day).

    Deterministic:
      - ordered by day
      - pure compute_timeline
    Idempotent:
      - upsert in cluster_daily_history keyed by (cluster_id, day)
    """
    freq_rows = _load_daily_frequencies(
        db,
        cluster_id=cluster_id,
        formula_version=formula_version,
        days=days,
    )
    if not freq_rows:
        return

    vols = [DailyVolume(day=r.day, volume=int(r.frequency)) for r in freq_rows]
    tl = compute_timeline(vols)

    payload = [
        {
            "day": p.day,
            "volume": p.volume,
            "growth_rate": p.growth_rate,
            "velocity": p.velocity,
            "breakout_flag": p.breakout_flag,
        }
        for p in tl
    ]

    persist_cluster_daily_history(
        cluster_id=str(cluster_id),
        timeline_rows=payload,
    )
