from __future__ import annotations

from typing import Optional, List
from sqlalchemy import select, desc, and_

from db.session import session_scope
from db.models import PainCluster
from api_gateway.schemas.insights import TopPainOut
from api_gateway.schemas.build_signal import BuildSignalOut
from domain.scoring.build_signal import (
    compute_build_signal,
    BuildSignalInputs,
)


class InsightsService:

    def _serialize(self, rows) -> List[TopPainOut]:
        result = []

        for r in rows:
            signal = compute_build_signal(
                BuildSignalInputs(
                    exploitability_score=r.exploitability_score,
                    exploitability_tier=r.exploitability_tier,
                    opportunity_window_status=r.opportunity_window_status,
                    breakout_score=r.breakout_score,
                    confidence_score=r.confidence_score,
                    saturation_score=r.saturation_score,
                    contradiction_score=r.contradiction_score,
                )
            )

            result.append(
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
                    build_signal=BuildSignalOut(**signal.__dict__),
                )
            )

        return result
