# --- append below existing class content ---

    # ----------------------------
    # VENTUREOS EXPORT
    # ----------------------------

    def export_ventureos_payload(self, cluster_id: str):
        from domain.insights.ventureos_export_v1 import (
            build_ventureos_export_payload_v1,
            to_dict,
        )
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

        opportunity_score = int(cluster.exploitability_score or 0)

        timing_status = "stable"
        if cluster.breakout_score and cluster.breakout_score >= 4:
            timing_status = "breakout"
        elif cluster.opportunity_window_status:
            timing_status = cluster.opportunity_window_status

        payload = build_ventureos_export_payload_v1(
            cluster_id=str(cluster.id),
            persona=hypothesis.target_persona,
            pain=hypothesis.core_pain_statement,
            wedge=hypothesis.suggested_wedge,
            monetization=hypothesis.monetization_angle,
            validation_plan=hypothesis.early_validation_path,
            opportunity_score=opportunity_score,
            timing_status=timing_status,
            risks=hypothesis.risk_flags,
        )

        return to_dict(payload)

