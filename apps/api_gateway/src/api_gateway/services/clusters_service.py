from __future__ import annotations

from sqlalchemy.orm import Session

from db.models import PainCluster


def list_clusters(
    *,
    db: Session,
    vertical_id: int,
    limit: int,
    offset: int,
    cluster_version: str | None = None,
):
    """
    Return clusters with pagination.
    """
    q = db.query(PainCluster).filter(PainCluster.vertical_id == int(vertical_id))
    if cluster_version:
        q = q.filter(PainCluster.cluster_version == str(cluster_version))
    total = q.count()
    rows = (
        q.order_by(PainCluster.id.asc())
        .limit(int(limit))
        .offset(int(offset))
        .all()
    )
    return rows, int(total)
