import time
from dataclasses import dataclass


@dataclass
class RateLimiter:
    min_interval_s: float = 1.0
    _last_ts: float = 0.0

    def acquire(self) -> None:
        now = time.time()
        wait = self.min_interval_s - (now - self._last_ts)
        if wait > 0:
            time.sleep(wait)
        self._last_ts = time.time()
