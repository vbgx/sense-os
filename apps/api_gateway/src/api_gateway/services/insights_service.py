from __future__ import annotations

import json
from typing import Optional, List
from sqlalchemy import select, desc, and_

from db.session import session_scope
from db.models import PainCluster
from db.repos.cluster_daily_history import list_cluster_history

from api_gateway.schemas.insights import TopPainOut
from api_gateway.schemas.cluster_detail import (
    ClusterDetailOut,
    RepresentativeSignalOut,
    TimelinePointOut,
)
from api_gateway.schemas.build_signal import BuildSignalOut
from domain.scoring.build_signal import (
    compute_build_signal,
    BuildSignalInputs,
)


class InsightsService:

    # ----------------------------
    # DETAIL ENDPOINT
    # ----------------------------

    def get_cluster_detail(self, *, cluster_id: str) -> ClusterDetailOut:
        with session_scope() as s:
            cluster = s.get(PainCluster, cluster_id)

        if cluster is None:
            raise ValueError("Cluster not found")

        key_phrases = []
        if cluster.key_phrases_json:
            try:
                key_phrases = json.loads(cluster.key_phrases_json)
            except Exception:
                key_phrases = []

        representative_signals = []
        if cluster.top_signal_ids_json:
            try:
                ids = json.loads(cluster.top_signal_ids_json)
                for sid in ids:
                    representative_signals.append(
                        RepresentativeSignalOut(id=str(sid), text="")
                    )
            except Exception:
                representative_signals = []

        timeline_rows = list_cluster_history(cluster_id=cluster_id, days=90)
        timeline = [
            TimelinePointOut(
                date=r.day,
                volume=r.volume,
                growth_rate=r.growth_rate,
                velocity=r.velocity,
                breakout_flag=r.breakout_flag,
            )
            for r in timeline_rows
        ]

        return ClusterDetailOut(
            cluster_id=str(cluster.id),
            cluster_summary=cluster.cluster_summary,

            exploitability_score=cluster.exploitability_score,
            exploitability_tier=cluster.exploitability_tier,

            severity_score=cluster.severity_score,
            recurrence_score=cluster.recurrence_score,
            monetizability_score=cluster.monetizability_score,

            breakout_score=cluster.breakout_score,
            opportunity_window_status=cluster.opportunity_window_status,
            competitive_heat_score=cluster.competitive_heat_score,
            contradiction_score=cluster.contradiction_score,

            confidence_score=cluster.confidence_score,

            key_phrases=key_phrases,
            representative_signals=representative_signals,
            timeline=timeline,
        )
