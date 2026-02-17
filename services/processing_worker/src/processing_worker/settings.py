from __future__ import annotations

import os

try:
    from domain.versions import DEFAULT_ALGO_VERSION as _DEFAULT_ALGO_VERSION
except Exception:
    _DEFAULT_ALGO_VERSION = "heuristics_v1"


ALGO_VERSION = str(os.environ.get("ALGO_VERSION") or _DEFAULT_ALGO_VERSION)

SUPPORTED_LANGUAGES = [
    x.strip() for x in (os.environ.get("SUPPORTED_LANGUAGES") or "en,unknown").split(",") if x.strip()
]
SPAM_THRESHOLD = int(os.environ.get("SPAM_THRESHOLD") or "70")
VERTICAL_CLASSIFIER_THRESHOLD = float(os.environ.get("VERTICAL_CLASSIFIER_THRESHOLD") or "0.20")
