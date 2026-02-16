from __future__ import annotations

import os


FRESHNESS_LAMBDA_PER_DAY = float(os.environ.get("FRESHNESS_LAMBDA_PER_DAY") or "0.01")
FRESHNESS_FLOOR = float(os.environ.get("FRESHNESS_FLOOR") or "0.40")
