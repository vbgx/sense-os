from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta

from domain.scoring.freshness_decay import compute_freshness_weight, apply_freshness_to_score


def test_recent_signal_weight_is_high():
    now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(days=1)
    w = compute_freshness_weight(created_at=created_at, lambda_per_day=0.01, now=now)
    assert w > 0.98


def test_old_signal_weight_is_lower():
    now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(days=365 * 3)
    w = compute_freshness_weight(created_at=created_at, lambda_per_day=0.01, now=now)
    assert w < 0.10


def test_stable_for_same_inputs():
    now = datetime(2026, 2, 16, 12, 0, 0, tzinfo=timezone.utc)
    created_at = datetime(2025, 2, 16, 12, 0, 0, tzinfo=timezone.utc)
    a = compute_freshness_weight(created_at=created_at, lambda_per_day=0.02, now=now)
    b = compute_freshness_weight(created_at=created_at, lambda_per_day=0.02, now=now)
    assert math.isclose(a, b, rel_tol=0.0, abs_tol=0.0)


def test_apply_freshness_reduces_old_score():
    s = 80.0
    recent = apply_freshness_to_score(score_0_100=s, freshness_weight_0_1=0.95, floor=0.40)
    old = apply_freshness_to_score(score_0_100=s, freshness_weight_0_1=0.05, floor=0.40)
    assert old < recent
