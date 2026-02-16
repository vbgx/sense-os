from __future__ import annotations

import re


def extract_plain_text(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_comment_like_sections(summary: str) -> str:
    if not summary:
        return ""
    text = extract_plain_text(summary)
    return text
