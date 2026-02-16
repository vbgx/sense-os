from __future__ import annotations

import os


SUPPORTED_LANGUAGES = [x.strip() for x in (os.environ.get("SUPPORTED_LANGUAGES") or "en").split(",") if x.strip()]
