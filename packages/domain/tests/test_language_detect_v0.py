from __future__ import annotations

from domain.scoring.language_detect_v0 import detect_language_code


def test_detect_language_en_stable():
    s = "I built a B2B SaaS and hit $10k MRR. Here is the exact onboarding process."
    a = detect_language_code(text=s)
    b = detect_language_code(text=s)
    assert a == b
    assert a in ("en", "unknown")


def test_detect_language_fr_stable():
    s = "J'ai créé un SaaS et j'ai atteint 10k MRR. Voici le process et les métriques."
    a = detect_language_code(text=s)
    b = detect_language_code(text=s)
    assert a == b
    assert a in ("fr", "unknown")
