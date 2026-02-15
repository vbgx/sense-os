from __future__ import annotations

from typing import Iterable

from sqlalchemy import Integer, bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session


def link_many(db: Session, *, cluster_id: int, pain_instance_ids: Iterable[int]) -> int:
    """
    🔗 Link a cluster to many pain_instances (idempotent).

    Uses ON CONFLICT DO NOTHING.
    ✅ Does NOT commit; caller controls transaction.

    Returns best-effort inserted rows (driver rowcount).
    """
    ids = list(pain_instance_ids)
    if not ids:
        return 0

    stmt = (
        text(
            """
            INSERT INTO cluster_signals (cluster_id, pain_instance_id)
            SELECT :cluster_id, x.pain_instance_id
            FROM unnest(:pain_ids) AS x(pain_instance_id)
            ON CONFLICT DO NOTHING
            """
        )
        .bindparams(bindparam("pain_ids", type_=ARRAY(Integer)))
    )

    res = db.execute(stmt, {"cluster_id": cluster_id, "pain_ids": ids})
    return int(getattr(res, "rowcount", 0) or 0)
