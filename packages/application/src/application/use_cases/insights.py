from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence

from application.ports import NotFoundError, UnitOfWork
from domain.competition.external_solution_density_v1 import compute_competitive_density_score
from domain.competition.keyword_saturation_v0 import compute_keyword_saturation_score_v0
from domain.competition.ph_overlap_v0 import compute_ph_overlap_score_v0
from domain.competition.repo_density_v0 import compute_repo_density_score_v0
from domain.scoring.build_signal import BuildSignalInputs, compute_build_signal
from domain.scoring.exploitability import ExploitabilityInputs
from domain.scoring.exploitability_v2 import compute_exploitability_v2


def _safe_json_list(raw: Optional[str]) -> List:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    return data if isinstance(data, list) else []


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


@dataclass(frozen=True)
class ClusterInsightSnapshot:
    dominant_persona: str
    cluster_summary: Optional[str]
    key_phrases: List[str]
    representative_signals: List[str]
    severity_score: int
    recurrence_score: int
    monetizability_score: int
    breakout_score: int
    opportunity_window_status: str
    contradiction_score: int
    competitive_heat_score: int
    saturation_score: int
    confidence_score: int
    exploitability_score: int


def _map_timing_status(opportunity_window_status: str, breakout_score: int) -> str:
    status = (opportunity_window_status or "").upper()
    if status == "EARLY":
        return "emerging"
    if status == "PEAK":
        return "stable"
    if status == "SATURATING":
        return "declining"
    if breakout_score >= 70:
        return "breakout"
    if breakout_score >= 40:
        return "emerging"
    return "stable"


def _compute_opportunity_score(scores: Sequence[int]) -> int:
    if not scores:
        return 0
    return int(round(sum(scores) / len(scores)))


@dataclass
class InsightsUseCase:
    uow: UnitOfWork

    def _cluster_to_top_pain(self, cluster: Any) -> dict[str, Any]:
        build_signal = compute_build_signal(
            BuildSignalInputs(
                exploitability_score=int(_get(cluster, "exploitability_score", 0) or 0),
                exploitability_tier=str(_get(cluster, "exploitability_tier", "") or ""),
                opportunity_window_status=str(_get(cluster, "opportunity_window_status", "") or ""),
                breakout_score=int(_get(cluster, "breakout_score", 0) or 0),
                confidence_score=int(_get(cluster, "confidence_score", 0) or 0),
                saturation_score=int(_get(cluster, "saturation_score", 0) or 0),
                contradiction_score=int(_get(cluster, "contradiction_score", 0) or 0),
            )
        )

        return {
            "cluster_id": str(_get(cluster, "id")),
            "vertical_id": str(_get(cluster, "vertical_id")) if _get(cluster, "vertical_id") is not None else None,
            "cluster_summary": _get(cluster, "cluster_summary"),
            "exploitability_score": int(_get(cluster, "exploitability_score", 0) or 0),
            "exploitability_tier": str(_get(cluster, "exploitability_tier", "") or ""),
            "severity_score": int(_get(cluster, "severity_score", 0) or 0),
            "breakout_score": int(_get(cluster, "breakout_score", 0) or 0),
            "saturation_score": int(_get(cluster, "saturation_score", 0) or 0),
            "opportunity_window_status": str(_get(cluster, "opportunity_window_status", "") or ""),
            "confidence_score": int(_get(cluster, "confidence_score", 0) or 0),
            "dominant_persona": str(_get(cluster, "dominant_persona", "") or ""),
            "build_signal": {
                "recommendation": build_signal.recommendation,
                "reasoning_summary": build_signal.reasoning_summary,
                "top_positive_factors": build_signal.top_positive_factors,
                "top_risk_factors": build_signal.top_risk_factors,
            },
        }

    def _list_top_pains(
        self,
        *,
        vertical_id: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        opportunity_window_status: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        with self.uow:
            rows = self.uow.pain_clusters.list_top_pains(
                vertical_id=vertical_id,
                tier=tier,
                limit=int(limit),
                offset=int(offset),
                opportunity_window_status=opportunity_window_status,
            )
        return [self._cluster_to_top_pain(r) for r in rows]

    def get_top_pains(
        self,
        *,
        vertical_id: Optional[str] = None,
        tier: Optional[str] = None,
        emerging_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        status = "EARLY" if emerging_only else None
        return self._list_top_pains(
            vertical_id=vertical_id,
            tier=tier,
            limit=limit,
            offset=offset,
            opportunity_window_status=status,
        )

    def get_emerging_opportunities(
        self,
        *,
        vertical_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return self._list_top_pains(
            vertical_id=vertical_id,
            limit=limit,
            offset=offset,
            opportunity_window_status="EARLY",
        )

    def get_declining_risks(
        self,
        *,
        vertical_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return self._list_top_pains(
            vertical_id=vertical_id,
            limit=limit,
            offset=offset,
            opportunity_window_status="SATURATING",
        )

    def get_cluster_detail(self, *, cluster_id: str) -> dict[str, Any]:
        with self.uow:
            try:
                cluster = self.uow.pain_clusters.get(cluster_id)
            except KeyError as exc:
                raise NotFoundError("Cluster not found") from exc

        if cluster is None:
            raise NotFoundError("Cluster not found")

        key_phrases = []
        raw_key_phrases = _get(cluster, "key_phrases_json")
        if raw_key_phrases:
            try:
                key_phrases = json.loads(raw_key_phrases)
            except Exception:
                key_phrases = []

        representative_signals: list[dict[str, Any]] = []
        raw_signal_ids = _get(cluster, "top_signal_ids_json")
        if raw_signal_ids:
            try:
                ids = json.loads(raw_signal_ids)
                for sid in ids:
                    representative_signals.append({"id": str(sid), "text": ""})
            except Exception:
                representative_signals = []

        with self.uow:
            timeline_rows = self.uow.cluster_daily_history.list_cluster_history(cluster_id=cluster_id, days=90)

        timeline = [
            {
                "date": r.day,
                "volume": r.volume,
                "growth_rate": r.growth_rate,
                "velocity": r.velocity,
                "breakout_flag": r.breakout_flag,
            }
            for r in timeline_rows
        ]

        competition_density = compute_competitive_density_score(
            [s.get("text", "") for s in representative_signals],
            key_phrases,
        )

        ph = compute_ph_overlap_score_v0(
            _get(cluster, "cluster_summary", "") or "",
            Path("tools/fixtures/competition/producthunt_snapshot_v0.jsonl"),
        )

        repo = compute_repo_density_score_v0(
            _get(cluster, "cluster_summary", "") or "",
            key_phrases,
            Path("tools/fixtures/competition/github_repos_snapshot_v0.jsonl"),
        )

        kw = compute_keyword_saturation_score_v0(
            key_phrases,
            Path("tools/fixtures/competition/keyword_index_snapshot_v0.json"),
        )

        inputs = ExploitabilityInputs(
            severity_score=_get(cluster, "severity_score"),
            recurrence_score=_get(cluster, "recurrence_score"),
            monetizability_score=_get(cluster, "monetizability_score"),
            breakout_score=_get(cluster, "breakout_score"),
            opportunity_window_score=_get(cluster, "opportunity_window_score"),
            half_life_days=_get(cluster, "half_life_days"),
            contradiction_score=_get(cluster, "contradiction_score"),
            competitive_heat_score=_get(cluster, "competitive_heat_score"),
            saturation_score=_get(cluster, "saturation_score"),
            opportunity_window_status=_get(cluster, "opportunity_window_status"),
        )

        v2, _ = compute_exploitability_v2(
            inputs,
            competitive_density_score=competition_density,
            ph_overlap_score=ph.ph_overlap_score,
            repo_density_score=repo.repo_density_score,
            keyword_saturation_score=kw.keyword_saturation_score,
        )

        return {
            "cluster_id": str(_get(cluster, "id")),
            "cluster_summary": _get(cluster, "cluster_summary"),

            "exploitability_score": _get(cluster, "exploitability_score"),
            "exploitability_tier": _get(cluster, "exploitability_tier"),
            "exploitability_score_v2": v2.exploitability_score,
            "exploitability_tier_v2": str(v2.exploitability_tier),
            "exploitability_version_v2": v2.exploitability_version,

            "severity_score": _get(cluster, "severity_score"),
            "recurrence_score": _get(cluster, "recurrence_score"),
            "monetizability_score": _get(cluster, "monetizability_score"),

            "breakout_score": _get(cluster, "breakout_score"),
            "opportunity_window_status": _get(cluster, "opportunity_window_status"),
            "competitive_heat_score": _get(cluster, "competitive_heat_score"),
            "contradiction_score": _get(cluster, "contradiction_score"),

            "confidence_score": _get(cluster, "confidence_score"),

            "key_phrases": key_phrases,
            "representative_signals": representative_signals,
            "timeline": timeline,
        }

    def generate_build_hypothesis(self, cluster_id: str):
        from domain.insights.build_hypothesis import BuildHypothesisInputs, compute_build_hypothesis

        with self.uow:
            try:
                cluster = self.uow.pain_clusters.get(cluster_id)
            except KeyError as exc:
                raise NotFoundError("Cluster not found") from exc

        if cluster is None:
            raise NotFoundError("Cluster not found")

        key_phrases = []
        raw_key_phrases = _get(cluster, "key_phrases_json")
        if raw_key_phrases:
            try:
                key_phrases = json.loads(raw_key_phrases)
            except Exception:
                key_phrases = []

        hypothesis = compute_build_hypothesis(
            BuildHypothesisInputs(
                dominant_persona=_get(cluster, "dominant_persona"),
                cluster_summary=_get(cluster, "cluster_summary"),
                key_phrases=key_phrases,
                exploitability_tier=_get(cluster, "exploitability_tier"),
                breakout_score=_get(cluster, "breakout_score"),
                contradiction_score=_get(cluster, "contradiction_score"),
            )
        )

        return hypothesis.__dict__.copy()

    def export_ventureos_payload(self, cluster_id: str) -> dict[str, Any]:
        from domain.insights.core_pain_statement_v1 import generate_core_pain_statement
        from domain.insights.early_validation_path_v1 import generate_early_validation_path
        from domain.insights.monetization_angle_v1 import generate_monetization_angle
        from domain.insights.risk_flags_v1 import generate_risk_flags
        from domain.insights.suggested_wedge_v1 import generate_suggested_wedge
        from domain.insights.target_persona_v1 import generate_target_persona
        from domain.insights.ventureos_export_v1 import build_ventureos_export_payload_v1, to_dict

        with self.uow:
            try:
                cluster = self.uow.pain_clusters.get(cluster_id)
            except KeyError as exc:
                raise NotFoundError("Cluster not found") from exc

            if cluster is None:
                raise NotFoundError("Cluster not found")

            key_phrases = [
                item for item in _safe_json_list(_get(cluster, "key_phrases_json"))
                if isinstance(item, str) and item.strip()
            ]

            signal_ids_raw = _safe_json_list(_get(cluster, "top_signal_ids_json"))
            signal_ids: List[int] = []
            for item in signal_ids_raw:
                if isinstance(item, int):
                    signal_ids.append(item)
                elif isinstance(item, str) and item.isdigit():
                    signal_ids.append(int(item))

            representative_signals: List[str] = []
            if signal_ids:
                rows = self.uow.signals.get_by_ids(signal_ids)
                signal_map = {int(_get(row, "id")): _get(row, "content") for row in rows if _get(row, "content")}
                representative_signals = [signal_map[sid] for sid in signal_ids if sid in signal_map]

            snapshot = ClusterInsightSnapshot(
                dominant_persona=str(_get(cluster, "dominant_persona", "") or ""),
                cluster_summary=_get(cluster, "cluster_summary"),
                key_phrases=key_phrases,
                representative_signals=representative_signals,
                severity_score=int(_get(cluster, "severity_score", 0) or 0),
                recurrence_score=int(_get(cluster, "recurrence_score", 0) or 0),
                monetizability_score=int(_get(cluster, "monetizability_score", 0) or 0),
                breakout_score=int(_get(cluster, "breakout_score", 0) or 0),
                opportunity_window_status=str(_get(cluster, "opportunity_window_status", "") or ""),
                contradiction_score=int(_get(cluster, "contradiction_score", 0) or 0),
                competitive_heat_score=int(_get(cluster, "competitive_heat_score", 0) or 0),
                saturation_score=int(_get(cluster, "saturation_score", 0) or 0),
                confidence_score=int(_get(cluster, "confidence_score", 0) or 0),
                exploitability_score=int(_get(cluster, "exploitability_score", 0) or 0),
            )

        persona_result = generate_target_persona(snapshot)
        persona = persona_result.primary_persona
        pain = generate_core_pain_statement(snapshot, persona)
        wedge = generate_suggested_wedge(snapshot, persona, pain).description
        monetization = generate_monetization_angle(snapshot, persona).model
        validation_plan = generate_early_validation_path(snapshot, persona).steps
        risks = generate_risk_flags(snapshot)
        timing_status = _map_timing_status(
            snapshot.opportunity_window_status,
            snapshot.breakout_score,
        )
        opportunity_score = _compute_opportunity_score(
            [
                snapshot.exploitability_score,
                snapshot.severity_score,
                snapshot.recurrence_score,
                snapshot.monetizability_score,
            ]
        )

        payload = build_ventureos_export_payload_v1(
            cluster_id=str(_get(cluster, "id")),
            persona=persona,
            pain=pain,
            wedge=wedge,
            monetization=monetization,
            validation_plan=validation_plan,
            opportunity_score=opportunity_score,
            timing_status=timing_status,
            risks=risks,
        )

        return to_dict(payload)
