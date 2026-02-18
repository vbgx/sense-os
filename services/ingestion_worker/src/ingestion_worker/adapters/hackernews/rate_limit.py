from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class SimpleRateLimiter:
    rate_per_s: float = 2.0  # keep it polite
    burst: float = 2.0

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._tokens = float(self.burst)
        self._last = time.monotonic()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now

                self._tokens = min(self.burst, self._tokens + elapsed * self.rate_per_s)

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return

                wait_s = (1.0 - self._tokens) / self.rate_per_s

            time.sleep(max(0.0, wait_s))


HN_ALGOLIA_LIMITER = SimpleRateLimiter()
