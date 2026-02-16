import re


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def _extract_root_cause(text: str) -> str:
    patterns = ["because", "due to", "caused by"]

    lower = text.lower()

    for p in patterns:
        if p in lower:
            parts = lower.split(p, 1)
            return _clean_text(parts[1])

    return ""


def generate_core_pain_statement(cluster, target_persona: str) -> str:
    summary = cluster.cluster_summary or ""
    key_phrases = cluster.key_phrases or []
    severity = cluster.severity_score or 0

    base_text = summary if summary else " ".join(key_phrases[:2])
    base_text = _clean_text(base_text)

    root_cause = _extract_root_cause(base_text)

    if not root_cause:
        if severity >= 4:
            root_cause = "repeated manual and fragmented workflows"
        elif severity >= 3:
            root_cause = "persistent manual processes"
        else:
            root_cause = "inefficient workflows"

    # Remove root clause from pain if present
    for connector in ["because", "due to", "caused by"]:
        if connector in base_text.lower():
            base_text = base_text.lower().split(connector, 1)[0]
            break

    pain = base_text.strip().rstrip(".")

    if severity >= 4:
        pain = f"significant {pain}"
    elif severity >= 3:
        pain = f"persistent {pain}"

    statement = f"{target_persona} struggle with {pain} because {root_cause}"

    return _clean_text(statement)

