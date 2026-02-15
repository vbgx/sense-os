from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from db.models import PainCluster


def clusters_exist_for_version(db: Session, vertical_id: int, cluster_version: str) -> bool:
    n = (
        db.query(func.count(PainCluster.id))
        .filter(PainCluster.vertical_id == int(vertical_id))
        .filter(PainCluster.cluster_version == str(cluster_version))
        .scalar()
        or 0
    )
    return n > 0


def upsert_cluster(
    db: Session,
    *,
    vertical_id: int,
    cluster_version: str,
    cluster_key: str,
    title: str,
    size: int,
):
    """
    Backward-compatible upsert.

    Returns (obj, created) where created=True only when inserted.
    Updates are applied idempotently but do not change the return shape.
    """
    obj, created, _updated = upsert_cluster_verbose(
        db,
        vertical_id=vertical_id,
        cluster_version=cluster_version,
        cluster_key=cluster_key,
        title=title,
        size=size,
    )
    return obj, created


def upsert_cluster_verbose(
    db: Session,
    *,
    vertical_id: int,
    cluster_version: str,
    cluster_key: str,
    title: str,
    size: int,
):
    """
    Strict upsert (atomic). Returns (obj, inserted, updated).
    Natural identity enforced by uq_pain_clusters_version_key:
      (vertical_id, cluster_version, cluster_key)
    """
    vertical_id = int(vertical_id)
    cluster_version = str(cluster_version)
    cluster_key = str(cluster_key)

    title = (title or "").strip()
    if not title:
        title = "(untitled)"
    title = title[:255]
    size = int(size)

    obj = PainCluster(
        vertical_id=vertical_id,
        cluster_version=cluster_version,
        cluster_key=cluster_key,
        title=title,
        size=size,
    )
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj, True, False
    except IntegrityError:
        db.rollback()

    existing = (
        db.query(PainCluster)
        .filter(PainCluster.vertical_id == vertical_id)
        .filter(PainCluster.cluster_version == cluster_version)
        .filter(PainCluster.cluster_key == cluster_key)
        .one()
    )

    updated = False
    if existing.title != title:
        existing.title = title
        updated = True
    if existing.size != size:
        existing.size = size
        updated = True

    if updated:
        db.add(existing)
        db.commit()
        db.refresh(existing)

    return existing, False, updated


def list_clusters_for_version(
    db: Session,
    *,
    cluster_version: str,
    vertical_id: int | None = None,
) -> list[PainCluster]:
    q = db.query(PainCluster).filter(PainCluster.cluster_version == str(cluster_version))
    if vertical_id is not None:
        q = q.filter(PainCluster.vertical_id == int(vertical_id))
    return q.order_by(PainCluster.id.asc()).all()
