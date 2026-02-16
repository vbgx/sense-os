from clustering_worker.clustering.confidence import (
    ConfidenceInputs,
    compute_confidence_score,
)


def test_small_noisy_cluster_low_confidence():
    score = compute_confidence_score(
        ConfidenceInputs(
            size=2,
            intra_similarity=0.2,
            silhouette_score=-0.3,
            noise_ratio=0.8,
        )
    )
    assert score < 40


def test_large_coherent_cluster_high_confidence():
    score = compute_confidence_score(
        ConfidenceInputs(
            size=50,
            intra_similarity=0.9,
            silhouette_score=0.7,
            noise_ratio=0.05,
        )
    )
    assert score > 80


def test_stability():
    inp = ConfidenceInputs(
        size=20,
        intra_similarity=0.6,
        silhouette_score=0.5,
        noise_ratio=0.1,
    )
    assert compute_confidence_score(inp) == compute_confidence_score(inp)
