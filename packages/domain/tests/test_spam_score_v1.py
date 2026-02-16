from domain.scoring.spam_score_v1 import compute_spam_score


def test_promotional_post_scores_high():
    s = "Sign up now! Buy now! Limited offer! https://promo.com https://promo.com"
    assert compute_spam_score(content=s) >= 60


def test_repeated_word_scores_high():
    s = "buy buy buy buy buy buy buy"
    assert compute_spam_score(content=s) >= 60


def test_legitimate_case_study_not_flagged():
    s = """
    I built a SaaS and reached $12k MRR.
    We reduced churn by 18% over 3 months.
    Here's the exact onboarding experiment we ran.
    """
    assert compute_spam_score(content=s) < 50
