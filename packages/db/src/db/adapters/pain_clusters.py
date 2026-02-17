from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from db.models import PainCluster
from db.repos.pain_clusters import PainClustersRepo


class PainClustersAdapter:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = PainClustersRepo(session=session)

    def list(self) -> list[PainCluster]:
        return self._repo.list()

    def get(self, cluster_id: str) -> PainCluster:
        return self._repo.get(cluster_id)

    def list_top_pains(
        self,
        *,
        vertical_id: str | None,
        tier: str | None,
        limit: int,
        offset: int,
        opportunity_window_status: str | None,
    ) -> list[PainCluster]:
        stmt = select(PainCluster)

        if vertical_id:
            try:
                stmt = stmt.where(PainCluster.vertical_id == int(vertical_id))
            except Exception:
                stmt = stmt.where(PainCluster.vertical_id == -1)

        if tier:
            stmt = stmt.where(PainCluster.exploitability_tier == str(tier))

        if opportunity_window_status:
            stmt = stmt.where(PainCluster.opportunity_window_status == str(opportunity_window_status))

        stmt = stmt.order_by(desc(PainCluster.exploitability_score), PainCluster.id.asc())
        stmt = stmt.limit(int(limit)).offset(int(offset))

        return list(self._session.execute(stmt).scalars().all())
