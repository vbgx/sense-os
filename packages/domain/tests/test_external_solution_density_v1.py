from domain.competition.external_solution_density_v1 import compute_competitive_density_score


def test_high_density_multiple_tools():
    signals = [
        "We switched to Shopify",
        "Already using Stripe",
        "Moved to Klaviyo",
        "Considering HubSpot as alternative",
        "Powered by Zapier",
    ]
    key_phrases = ["software migration", "platform switch"]

    score = compute_competitive_density_score(signals, key_phrases)

    assert score > 40


def test_low_density_no_solution_mentions():
    signals = [
        "Manual reconciliation is painful",
        "Workflow is chaotic",
    ]
    key_phrases = ["manual process"]

    score = compute_competitive_density_score(signals, key_phrases)

    assert score < 20


def test_stability_between_runs():
    signals = ["Using Shopify and Stripe"]
    key_phrases = []

    s1 = compute_competitive_density_score(signals, key_phrases)
    s2 = compute_competitive_density_score(signals, key_phrases)

    assert s1 == s2

