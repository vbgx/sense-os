from dataclasses import dataclass
from typing import List


@dataclass
class EarlyValidationPathResult:
    steps: List[str]


def _detect_channel_context(cluster):
    text = (
        (cluster.cluster_summary or "") + " " +
        " ".join(cluster.key_phrases or []) + " " +
        " ".join(cluster.representative_signals or [])
    ).lower()

    channels = []

    if "reddit" in text:
        channels.append("reddit")

    if "twitter" in text or "x.com" in text:
        channels.append("twitter")

    if "linkedin" in text:
        channels.append("linkedin")

    if "shopify" in text:
        channels.append("shopify")

    if "saas" in text:
        channels.append("saas")

    return channels


def generate_early_validation_path(cluster, target_persona: str):
    persona = target_persona
    channels = _detect_channel_context(cluster)

    steps = []

    # Step 1 — Landing page test
    steps.append(
        f"Launch a simple landing page targeting {persona} with a clear value proposition and collect 20+ email signups."
    )

    # Step 2 — Direct outreach (persona-specific)
    if "linkedin" in channels:
        steps.append(
            f"Send 30 targeted LinkedIn DMs to {persona} describing the specific pain and asking for 15-min feedback calls."
        )
    elif "reddit" in channels:
        steps.append(
            f"Post a structured validation question in relevant subreddits where {persona} are active and measure engagement."
        )
    else:
        steps.append(
            f"Send 30 cold emails or DMs to {persona} asking about their current workflow and willingness to try a solution."
        )

    # Step 3 — No-code MVP or manual test
    steps.append(
        f"Build a lightweight no-code MVP (Notion/Zapier/Airtable) solving one narrow friction point for {persona} and onboard 3 beta users."
    )

    return EarlyValidationPathResult(steps=steps)

