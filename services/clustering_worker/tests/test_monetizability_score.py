from __future__ import annotations

from domain.models.persona import Persona
from domain.scoring.monetizability import MonetizabilitySignal, compute_monetizability_score


def test_business_pain_scores_high():
    signals = [
        MonetizabilitySignal(
            text="Our SaaS MRR is down due to churn. Stripe payouts failing is causing revenue loss.",
            persona=Persona.founder,
        ),
        MonetizabilitySignal(
            text="Billing and invoices are broken; customers cannot pay. Cash flow impact is real.",
            persona=Persona.founder,
        ),
    ]
    s = compute_monetizability_score(signals)
    assert s >= 50


def test_hobby_frustration_scores_low():
    signals = [
        MonetizabilitySignal(
            text="I'm just learning, my side project is for fun. This tutorial is confusing.",
            persona=Persona.hobbyist,
        ),
        MonetizabilitySignal(
            text="Beginner question: my weekend project doesn't compile, any tips?",
            persona=Persona.hobbyist,
        ),
    ]
    s = compute_monetizability_score(signals)
    assert s <= 30


def test_score_is_bounded():
    extreme = [
        MonetizabilitySignal(
            text=("revenue loss mrr arr billing payment churn pricing " * 200),
            persona=Persona.founder,
        )
        for _ in range(200)
    ]
    s = compute_monetizability_score(extreme)
    assert 0 <= s <= 100
