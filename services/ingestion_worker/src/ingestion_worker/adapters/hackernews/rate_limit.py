from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RateLimiter:
    min_interval_s: float
    _last_ts: float = 0.0

    def wait(self) -> None:
        now = time.time()
        elapsed = now - self._last_ts
        if elapsed < self.min_interval_s:
            time.sleep(self.min_interval_s - elapsed)
        self._last_ts = time.time()
