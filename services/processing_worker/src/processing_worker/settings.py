from __future__ import annotations

import os


SUPPORTED_LANGUAGES = [x.strip() for x in (os.environ.get("SUPPORTED_LANGUAGES") or "en").split(",") if x.strip()]
SPAM_THRESHOLD = int(os.environ.get("SPAM_THRESHOLD") or "70")

VERTICAL_CLASSIFIER_THRESHOLD = float(os.environ.get("VERTICAL_CLASSIFIER_THRESHOLD") or "0.20")
