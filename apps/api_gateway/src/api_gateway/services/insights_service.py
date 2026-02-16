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

from domain.scoring.exploitability import ExploitabilityInputs
from domain.scoring.exploitability_v2 import compute_exploitability_v2
from domain.competition.external_solution_density_v1 import compute_competitive_density_score
from domain.competition.ph_overlap_v0 import compute_ph_overlap_score_v0
from domain.competition.repo_density_v0 import compute_repo_density_score_v0
from domain.competition.keyword_saturation_v0 import compute_keyword_saturation_score_v0
from pathlib import Path


class InsightsService:

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

        competition_density = compute_competitive_density_score(
            [s.text for s in representative_signals],
            key_phrases,
        )

        ph = compute_ph_overlap_score_v0(
            cluster.cluster_summary or "",
            Path("tools/fixtures/competition/producthunt_snapshot_v0.jsonl"),
        )

        repo = compute_repo_density_score_v0(
            cluster.cluster_summary or "",
            key_phrases,
            Path("tools/fixtures/competition/github_repos_snapshot_v0.jsonl"),
        )

        kw = compute_keyword_saturation_score_v0(
            key_phrases,
            Path("tools/fixtures/competition/keyword_index_snapshot_v0.json"),
        )

        inputs = ExploitabilityInputs(
            severity_score=cluster.severity_score,
            recurrence_score=cluster.recurrence_score,
            monetizability_score=cluster.monetizability_score,
            breakout_score=cluster.breakout_score,
            opportunity_window_score=getattr(cluster, "opportunity_window_score", None),
            half_life_days=getattr(cluster, "half_life_days", None),
            contradiction_score=cluster.contradiction_score,
            competitive_heat_score=cluster.competitive_heat_score,
            saturation_score=getattr(cluster, "saturation_score", None),
            opportunity_window_status=cluster.opportunity_window_status,
        )

        v2, _ = compute_exploitability_v2(
            inputs,
            competitive_density_score=competition_density,
            ph_overlap_score=ph.ph_overlap_score,
            repo_density_score=repo.repo_density_score,
            keyword_saturation_score=kw.keyword_saturation_score,
        )

        return ClusterDetailOut(
            cluster_id=str(cluster.id),
            cluster_summary=cluster.cluster_summary,

            exploitability_score=cluster.exploitability_score,
            exploitability_tier=cluster.exploitability_tier,
            exploitability_score_v2=v2.exploitability_score,
            exploitability_tier_v2=str(v2.exploitability_tier),
            exploitability_version_v2=v2.exploitability_version,

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

    def generate_build_hypothesis(self, cluster_id: str):
        from domain.insights.build_hypothesis import (
            compute_build_hypothesis,
            BuildHypothesisInputs,
        )

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

        hypothesis = compute_build_hypothesis(
            BuildHypothesisInputs(
                dominant_persona=cluster.dominant_persona,
                cluster_summary=cluster.cluster_summary,
                key_phrases=key_phrases,
                exploitability_tier=cluster.exploitability_tier,
                breakout_score=cluster.breakout_score,
                contradiction_score=cluster.contradiction_score,
            )
        )

        from api_gateway.schemas.build_hypothesis import BuildHypothesisOut

        return BuildHypothesisOut(**hypothesis.__dict__)

