from domain.scoring.underserved_v1 import compute_underserved_factor_v1


def test_high_saturation_low_underserved():
    result = compute_underserved_factor_v1(
        competitive_density_score=90,
        ph_overlap_score=80,
        repo_density_score=85,
        keyword_saturation_score=88,
        competitive_heat_score=70,
    )

    assert result.underserved_factor <= 30


def test_low_saturation_high_underserved():
    result = compute_underserved_factor_v1(
        competitive_density_score=10,
        ph_overlap_score=5,
        repo_density_score=8,
        keyword_saturation_score=12,
        competitive_heat_score=15,
    )

    assert result.underserved_factor >= 70


def test_clamped_bounds():
    result = compute_underserved_factor_v1(
        competitive_density_score=200,
        ph_overlap_score=200,
        repo_density_score=200,
        keyword_saturation_score=200,
        competitive_heat_score=200,
    )

    assert 0 <= result.underserved_factor <= 100


def test_deterministic():
    r1 = compute_underserved_factor_v1(
        competitive_density_score=30,
        ph_overlap_score=40,
        repo_density_score=50,
        keyword_saturation_score=60,
        competitive_heat_score=20,
    )
    r2 = compute_underserved_factor_v1(
        competitive_density_score=30,
        ph_overlap_score=40,
        repo_density_score=50,
        keyword_saturation_score=60,
        competitive_heat_score=20,
    )

    assert r1.underserved_factor == r2.underserved_factor
    assert r1.version == r2.version
