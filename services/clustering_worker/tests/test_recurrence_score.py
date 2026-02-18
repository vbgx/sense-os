from __future__ import annotations

from datetime import datetime, timedelta, timezone

from domain.scoring.cluster.recurrence_v1 import InstanceForRecurrence, compute_cluster_recurrence


def _dt(days_ago: int) -> datetime:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=12, minute=0, second=0, microsecond=0)


def test_recurrence_empty_is_zero():
    s, r = compute_cluster_recurrence([])
    assert s == 0
    assert r == 0.0


def test_single_user_spam_low_score_even_if_many():
    instances = [
        InstanceForRecurrence(
            text="I keep having the same checkout bug on Shopify. It fails again and again.",
            user_id="user_1",
            source_id=f"post_{i}",
            created_at=_dt(0),
        )
        for i in range(40)
    ]
    score, _ = compute_cluster_recurrence(instances)
    assert score <= 30


def test_multi_user_same_pain_higher_score():
    instances = []
    for u in range(20):
        instances.append(
            InstanceForRecurrence(
                text="My checkout fails with Stripe and I cannot complete orders. Anyone else?",
                user_id=f"user_{u}",
                source_id=f"post_{u}",
                created_at=_dt(0),
            )
        )
    score, _ = compute_cluster_recurrence(instances)
    assert score >= 40


def test_distributed_over_time_scores_higher_than_spike():
    # spike: many users but same day
    spike = [
        InstanceForRecurrence(
            text="We cannot reconcile payouts; accounting mismatch is painful.",
            user_id=f"user_{i}",
            source_id=f"spike_{i}",
            created_at=_dt(0),
        )
        for i in range(20)
    ]

    # distributed: similar users but spread across days
    distributed = [
        InstanceForRecurrence(
            text="We cannot reconcile payouts; accounting mismatch is painful.",
            user_id=f"user_{i}",
            source_id=f"dist_{i}",
            created_at=_dt(i % 10),
        )
        for i in range(20)
    ]

    score_spike, _ = compute_cluster_recurrence(spike)
    score_dist, _ = compute_cluster_recurrence(distributed)

    assert score_dist > score_spike


def test_score_is_bounded_0_100():
    extreme = [
        InstanceForRecurrence(
            text=("same phrase " * 200),
            user_id=f"user_{i % 200}",
            source_id=f"post_{i}",
            created_at=_dt(i % 30),
        )
        for i in range(2000)
    ]
    score, ratio = compute_cluster_recurrence(extreme)
    assert 0 <= score <= 100
    assert 0.0 <= ratio <= 1.0
