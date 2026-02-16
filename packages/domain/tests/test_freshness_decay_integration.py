from __future__ import annotations

from datetime import datetime, timezone, timedelta

from domain.scoring.pain_severity import SeveritySignal, compute_pain_severity_index
from domain.scoring.recurrence import RecurrenceSignal, compute_recurrence


def test_severity_old_signals_weigh_less_than_recent():
    now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=timezone.utc)

    base_signals = [
        SeveritySignal(sentiment_compound=-0.6, upvotes=10, comments=3, replies=1, text="Detailed pain with context", created_at=now),
        SeveritySignal(sentiment_compound=-0.4, upvotes=5, comments=1, replies=0, text="More details and metrics 10% churn", created_at=now),
    ]

    recent = compute_pain_severity_index(
        base_signals,
        freshness_lambda_per_day=0.01,
        freshness_floor=0.40,
        now=now,
    )

    old_signals = [
        SeveritySignal(**{**base_signals[0].__dict__, "created_at": now - timedelta(days=365 * 3)}),
        SeveritySignal(**{**base_signals[1].__dict__, "created_at": now - timedelta(days=365 * 3)}),
    ]

    old = compute_pain_severity_index(
        old_signals,
        freshness_lambda_per_day=0.01,
        freshness_floor=0.40,
        now=now,
    )

    assert old < recent


def test_recurrence_old_signals_weigh_less_than_recent():
    now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=timezone.utc)

    recent_signals = [
        RecurrenceSignal(user_id="u1", created_at=now - timedelta(days=1), text="how do I handle onboarding churn"),
        RecurrenceSignal(user_id="u2", created_at=now - timedelta(days=2), text="onboarding churn is killing me"),
        RecurrenceSignal(user_id="u3", created_at=now - timedelta(days=3), text="pricing and churn issues in SaaS onboarding"),
    ]

    old_signals = [
        RecurrenceSignal(user_id="u1", created_at=now - timedelta(days=365 * 3 + 1), text="how do I handle onboarding churn"),
        RecurrenceSignal(user_id="u2", created_at=now - timedelta(days=365 * 3 + 2), text="onboarding churn is killing me"),
        RecurrenceSignal(user_id="u3", created_at=now - timedelta(days=365 * 3 + 3), text="pricing and churn issues in SaaS onboarding"),
    ]

    score_recent, _ = compute_recurrence(
        recent_signals,
        freshness_lambda_per_day=0.01,
        freshness_floor=0.40,
        now=now,
    )
    score_old, _ = compute_recurrence(
        old_signals,
        freshness_lambda_per_day=0.01,
        freshness_floor=0.40,
        now=now,
    )

    assert score_old < score_recent


def test_stable_given_same_now_and_inputs():
    now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=timezone.utc)
    signals = [
        SeveritySignal(sentiment_compound=-0.6, upvotes=10, comments=3, replies=1, text="pain", created_at=now - timedelta(days=10)),
        SeveritySignal(sentiment_compound=-0.2, upvotes=2, comments=0, replies=0, text="pain", created_at=now - timedelta(days=10)),
    ]
    a = compute_pain_severity_index(signals, freshness_lambda_per_day=0.02, freshness_floor=0.40, now=now)
    b = compute_pain_severity_index(signals, freshness_lambda_per_day=0.02, freshness_floor=0.40, now=now)
    assert a == b
