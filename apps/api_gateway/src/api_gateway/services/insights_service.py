from __future__ import annotations

from typing import Optional, List
from sqlalchemy import select, desc

from db.session import session_scope
from db.models import PainCluster
from api_gateway.schemas.insights import TopPainOut


class InsightsService:

    def get_top_pains(
        self,
        *,
        vertical_id: Optional[str],
        tier: Optional[str],
        emerging_only: bool,
        limit: int,
        offset: int,
    ) -> List[TopPainOut]:

        with session_scope() as s:
            stmt = select(PainCluster)

            if vertical_id:
                stmt = stmt.where(PainCluster.vertical_id == vertical_id)

            if tier:
                stmt = stmt.where(PainCluster.exploitability_tier == tier)

            if emerging_only:
                stmt = stmt.where(PainCluster.breakout_score > 0)

            stmt = stmt.order_by(
                desc(PainCluster.exploitability_score),
                desc(PainCluster.confidence_score),
            ).limit(limit).offset(offset)

            rows = s.execute(stmt).scalars().all()

        return [
            TopPainOut(
                cluster_id=str(r.id),
                cluster_summary=r.cluster_summary,
                exploitability_score=r.exploitability_score,
                exploitability_tier=r.exploitability_tier,
                severity_score=r.severity_score,
                breakout_score=r.breakout_score,
                opportunity_window_status=r.opportunity_window_status,
                confidence_score=r.confidence_score,
                dominant_persona=r.dominant_persona,
            )
            for r in rows
        ]
