from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class TokenBucketRateLimiter:
    rate_per_s: float = 0.5  # StackExchange can be strict; stay polite (1 req / 2s)
    burst: float = 1.0

    def __post_init__(self) -> None:
        if self.rate_per_s <= 0:
            raise ValueError("rate_per_s must be > 0")
        if self.burst <= 0:
            raise ValueError("burst must be > 0")
        self._lock = threading.Lock()
        self._tokens = float(self.burst)
        self._last = time.monotonic()

    def acquire(self, tokens: float = 1.0) -> None:
        if tokens <= 0:
            return

        while True:
            wait_s = 0.0
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now

                self._tokens = min(self.burst, self._tokens + elapsed * self.rate_per_s)

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return

                missing = tokens - self._tokens
                wait_s = missing / self.rate_per_s

            time.sleep(max(0.0, wait_s))


STACKEXCHANGE_LIMITER = TokenBucketRateLimiter()
