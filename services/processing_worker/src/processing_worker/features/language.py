from __future__ import annotations

from domain.scoring.language_detect_v0 import detect_language_code


def compute_language_code(*, content: str) -> str:
    return detect_language_code(text=content or "")
