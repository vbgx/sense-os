from __future__ import annotations

import re

try:
    from langdetect import detect as _ld_detect
    from langdetect.detector_factory import DetectorFactory as _DetectorFactory

    _DetectorFactory.seed = 0
    _HAS_LANGDETECT = True
except Exception:
    _HAS_LANGDETECT = False
    _ld_detect = None


_WORD_EN = re.compile(r"\b(the|and|is|are|how|what|why|with|from|to|in)\b", re.IGNORECASE)
_WORD_FR = re.compile(r"\b(le|la|les|est|pourquoi|avec|dans|des|une|un)\b", re.IGNORECASE)


def detect_language_code(*, text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "unknown"

    if _HAS_LANGDETECT:
        try:
            code = _ld_detect(t)
            return code or "unknown"
        except Exception:
            pass

    s = t.lower()
    en_hits = len(_WORD_EN.findall(s))
    fr_hits = len(_WORD_FR.findall(s))
    if en_hits == 0 and fr_hits == 0:
        return "unknown"
    return "en" if en_hits >= fr_hits else "fr"
