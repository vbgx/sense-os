from __future__ import annotations

from datetime import datetime, timedelta, timezone

from domain.scoring.contradiction import ContradictionSignal, compute_contradiction_index


def _dt(days_ago: int) -> datetime:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=12, minute=0, second=0, microsecond=0)


def test_homogeneous_cluster_low_contradiction():
    signals = [ContradictionSignal(sentiment_compound=-0.6, created_at=_dt(i % 2)) for i in range(30)]
    s = compute_contradiction_index(signals)
    assert s <= 30


def test_polarized_cluster_high_contradiction():
    signals = []
    for i in range(20):
        signals.append(ContradictionSignal(sentiment_compound=0.8, created_at=_dt(i % 3)))
    for i in range(20):
        signals.append(ContradictionSignal(sentiment_compound=-0.8, created_at=_dt(i % 3)))
    s = compute_contradiction_index(signals)
    assert s >= 50


def test_balanced_ratio_increases_polarization_component():
    # 90% negative should have lower contradiction than 50/50 when variance is similar
    mostly_neg = [ContradictionSignal(sentiment_compound=-0.8, created_at=_dt(0)) for _ in range(90)] + \
                 [ContradictionSignal(sentiment_compound=0.8, created_at=_dt(0)) for _ in range(10)]
    balanced = [ContradictionSignal(sentiment_compound=-0.8, created_at=_dt(0)) for _ in range(50)] + \
               [ContradictionSignal(sentiment_compound=0.8, created_at=_dt(0)) for _ in range(50)]

    s1 = compute_contradiction_index(mostly_neg)
    s2 = compute_contradiction_index(balanced)

    assert s2 > s1


def test_temporal_volatility_increases_score():
    # Alternate daily mean sentiment to increase volatility
    signals = []
    for d in range(10):
        v = 0.9 if d % 2 == 0 else -0.9
        for _ in range(10):
            signals.append(ContradictionSignal(sentiment_compound=v, created_at=_dt(d)))

    s = compute_contradiction_index(signals)
    assert s >= 40


def test_bounded_0_100():
    extreme = [ContradictionSignal(sentiment_compound=(1.0 if i % 2 == 0 else -1.0), created_at=_dt(i % 30)) for i in range(2000)]
    s = compute_contradiction_index(extreme)
    assert 0 <= s <= 100
