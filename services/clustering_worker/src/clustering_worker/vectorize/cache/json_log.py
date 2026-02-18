from __future__ import annotations

import json
from typing import Any


def log_json(logger: Any, event: str, payload: dict[str, Any]) -> None:
    """
    Emit a single-line JSON log. Safe for log shippers.
    """
    data = {"event": str(event), **payload}
    try:
        logger.info(json.dumps(data, ensure_ascii=False, sort_keys=True))
    except Exception:
        # Never fail clustering because of logging
        logger.info('{"event":"log_json_failed"}')
