from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from db.models import PainCluster


@dataclass
class PainClustersRepo:
    session: Session

    def list(self) -> list[PainCluster]:
        return (
            self.session.query(PainCluster)
            .order_by(PainCluster.severity_score.desc(), PainCluster.recurrence_score.desc(), PainCluster.size.desc())
            .all()
        )

    def get(self, cluster_id: str) -> PainCluster:
        obj = self.session.query(PainCluster).filter(PainCluster.id == cluster_id).one_or_none()
        if obj is None:
            raise KeyError(f"cluster not found: {cluster_id}")
        return obj

    def upsert(self, payload: dict[str, Any]) -> PainCluster:
        obj = self.session.query(PainCluster).filter(PainCluster.id == payload["id"]).one_or_none()
        if obj is None:
            obj = PainCluster(**payload)
            self.session.add(obj)
            self.session.commit()
            return obj

        for k, v in payload.items():
            setattr(obj, k, v)
        self.session.commit()
        return obj


def clusters_exist_for_version(
    db: Session,
    *,
    vertical_id: int,
    cluster_version: str,
) -> bool:
    return (
        db.query(PainCluster.id)
        .filter(PainCluster.vertical_id == int(vertical_id))
        .filter(PainCluster.cluster_version == str(cluster_version))
        .limit(1)
        .count()
        > 0
    )


def upsert_cluster(
    db: Session,
    *,
    vertical_id: int,
    cluster_version: str,
    cluster_key: str,
    title: str,
    size: int,
    **kwargs: Any,
) -> tuple[PainCluster, bool]:
    obj = (
        db.query(PainCluster)
        .filter(PainCluster.vertical_id == int(vertical_id))
        .filter(PainCluster.cluster_version == str(cluster_version))
        .filter(PainCluster.cluster_key == str(cluster_key))
        .one_or_none()
    )

    if obj is None:
        obj = PainCluster(
            vertical_id=int(vertical_id),
            cluster_version=str(cluster_version),
            cluster_key=str(cluster_key),
            title=str(title),
            size=int(size),
            **kwargs,
        )
        db.add(obj)
        db.flush()
        return obj, True

    obj.title = str(title)
    obj.size = int(size)
    for k, v in kwargs.items():
        setattr(obj, k, v)
    db.flush()
    return obj, False
