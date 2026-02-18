from __future__ import annotations

from domain.scoring.cluster.persona_v1 import InstanceForPersona, infer_cluster_persona_from_instances


def test_founder_markers_dominate():
    instances = [
        InstanceForPersona(text="My SaaS MRR dropped and churn increased after changing pricing."),
        InstanceForPersona(text="We are trying to reach PMF; CAC is too high and runway is short."),
        InstanceForPersona(text="Stripe payouts and pricing page experiments are killing retention."),
    ]
    inf = infer_cluster_persona_from_instances(instances)
    assert inf.dominant_persona.value in ("founder", "unknown")
    # For this synthetic test, we expect founder to be high confidence most of the time.
    assert inf.confidence >= 0.15


def test_operator_markers_dominate():
    instances = [
        InstanceForPersona(text="On-call incidents keep happening. Need a better runbook and SLOs."),
        InstanceForPersona(text="Kubernetes deploy pipeline is flaky. Observability gaps cause incidents."),
    ]
    inf = infer_cluster_persona_from_instances(instances)
    assert inf.dominant_persona.value in ("operator", "unknown")
    assert 0.0 <= inf.confidence <= 1.0


def test_low_signal_becomes_unknown():
    instances = [
        InstanceForPersona(text="Help needed."),
        InstanceForPersona(text="Any ideas?"),
    ]
    inf = infer_cluster_persona_from_instances(instances)
    assert inf.dominant_persona.value == "unknown"
