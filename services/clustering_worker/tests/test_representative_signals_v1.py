from __future__ import annotations

from clustering_worker.clustering.representative import (
    SignalCandidate,
    rank_representative_signal_ids,
)


def test_representative_ranking_is_deterministic_with_ties():
    cands = [
        SignalCandidate("s1", "u1", 0.10, 40, 10),
        SignalCandidate("s2", "u2", 0.10, 40, 10),
        SignalCandidate("s3", "u3", 0.10, 40, 10),
    ]
    a = rank_representative_signal_ids(cands, k=3, per_user_cap=1)
    b = rank_representative_signal_ids(cands, k=3, per_user_cap=1)
    assert a == b
    # tie-breaker by signal_id ASC
    assert a == ["s1", "s2", "s3"]


def test_representative_prefers_min_distance_then_severity_then_engagement():
    cands = [
        SignalCandidate("s_far", "u1", 0.80, 100, 999),
        SignalCandidate("s_close_lowsev", "u2", 0.10, 10, 0),
        SignalCandidate("s_close_highsev", "u3", 0.10, 90, 0),
        SignalCandidate("s_close_highsev_higheng", "u4", 0.10, 90, 50),
    ]
    out = rank_representative_signal_ids(cands, k=3, per_user_cap=1)
    assert out[0] == "s_close_highsev_higheng"
    assert out[1] == "s_close_highsev"
    assert out[2] == "s_close_lowsev"


def test_representative_avoids_single_user_dominance_then_relaxes():
    # 5 best signals all from same user; we cap per user to 1
    cands = [
        SignalCandidate("s1", "u1", 0.01, 50, 10),
        SignalCandidate("s2", "u1", 0.02, 49, 9),
        SignalCandidate("s3", "u1", 0.03, 48, 8),
        SignalCandidate("s4", "u2", 0.50, 10, 1),
        SignalCandidate("s5", "u3", 0.60, 10, 1),
    ]
    out = rank_representative_signal_ids(cands, k=4, per_user_cap=1)
    # First pass: s1 (u1), then include u2/u3, then relax to fill k
    assert out[0] == "s1"
    assert "s4" in out
    assert "s5" in out
    assert len(out) == 4
