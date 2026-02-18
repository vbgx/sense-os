from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class SimpleRateLimiter:
    rate_per_s: float = 0.5  # 1 request every 2 seconds
    burst: float = 1.0

    def __post_init__(self):
        self._lock = threading.Lock()
        self._tokens = self.burst
        self._last = time.monotonic()

    def acquire(self):
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now

                self._tokens = min(self.burst, self._tokens + elapsed * self.rate_per_s)

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return

                wait = (1.0 - self._tokens) / self.rate_per_s

            time.sleep(wait)


GDELT_LIMITER = SimpleRateLimiter()
