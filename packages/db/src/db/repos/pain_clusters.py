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
            .order_by(PainCluster.severity_score.desc(), PainCluster.size.desc())
            .all()
        )

    def get(self, cluster_id: str) -> PainCluster:
        obj = self.session.query(PainCluster).filter(PainCluster.id == cluster_id).one_or_none()
        if obj is None:
            raise KeyError(f"cluster not found: {cluster_id}")
        return obj

    def upsert(self, payload: dict[str, Any]) -> PainCluster:
        """
        payload expects at least: id, vertical_id, title, size, severity_score
        """
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
