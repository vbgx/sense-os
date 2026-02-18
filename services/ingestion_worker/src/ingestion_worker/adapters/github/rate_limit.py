from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class TokenBucketRateLimiter:
    rate_per_s: float = 1.0
    burst: float = 1.0

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._tokens = self.burst
        self._last = time.monotonic()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                delta = now - self._last
                self._last = now

                self._tokens = min(self.burst, self._tokens + delta * self.rate_per_s)

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return

                wait = (1.0 - self._tokens) / self.rate_per_s

            time.sleep(wait)


GITHUB_LIMITER = TokenBucketRateLimiter()
