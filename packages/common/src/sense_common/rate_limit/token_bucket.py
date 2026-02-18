from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    rate_per_s: float
    capacity: int
    tokens: float = 0.0
    last_t: float = 0.0

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)
        self.last_t = time.monotonic()

    def consume(self, n: int = 1) -> None:
        while True:
            now = time.monotonic()
            dt = max(0.0, now - self.last_t)
            self.last_t = now
            self.tokens = min(float(self.capacity), self.tokens + dt * float(self.rate_per_s))
            if self.tokens >= n:
                self.tokens -= n
                return
            time.sleep(max(0.01, (n - self.tokens) / max(1e-6, self.rate_per_s)))
