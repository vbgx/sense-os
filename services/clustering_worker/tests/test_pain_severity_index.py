from __future__ import annotations

from clustering_worker.storage.severity import InstanceForSeverity, compute_cluster_severity


def test_severity_empty_is_zero():
    assert compute_cluster_severity([]) == 0


def test_severity_increases_with_frequency():
    low = [InstanceForSeverity(text="x", sentiment_compound=-0.2, upvotes=0, comments=0, replies=0) for _ in range(3)]
    high = [InstanceForSeverity(text="x", sentiment_compound=-0.2, upvotes=0, comments=0, replies=0) for _ in range(60)]
    assert compute_cluster_severity(high) > compute_cluster_severity(low)


def test_severity_increases_with_negative_intensity():
    weak = [InstanceForSeverity(text="x", sentiment_compound=-0.1, upvotes=0, comments=0, replies=0) for _ in range(20)]
    strong = [InstanceForSeverity(text="x", sentiment_compound=-0.9, upvotes=0, comments=0, replies=0) for _ in range(20)]
    assert compute_cluster_severity(strong) > compute_cluster_severity(weak)


def test_severity_increases_with_engagement():
    low = [InstanceForSeverity(text="x", sentiment_compound=-0.4, upvotes=1, comments=0, replies=0) for _ in range(15)]
    high = [InstanceForSeverity(text="x", sentiment_compound=-0.4, upvotes=200, comments=50, replies=10) for _ in range(15)]
    assert compute_cluster_severity(high) > compute_cluster_severity(low)


def test_severity_increases_with_specificity():
    short = [InstanceForSeverity(text="short", sentiment_compound=-0.4, upvotes=0, comments=0, replies=0) for _ in range(20)]
    long = [InstanceForSeverity(text=("very detailed " * 80), sentiment_compound=-0.4, upvotes=0, comments=0, replies=0) for _ in range(20)]
    assert compute_cluster_severity(long) > compute_cluster_severity(short)


def test_severity_is_bounded_0_100():
    extreme = [
        InstanceForSeverity(
            text=("very detailed " * 500),
            sentiment_compound=-1.0,
            upvotes=10_000,
            comments=10_000,
            replies=10_000,
        )
        for _ in range(1000)
    ]
    s = compute_cluster_severity(extreme)
    assert 0 <= s <= 100
