import time
import threading
from dataclasses import dataclass


@dataclass
class SimpleRateLimiter:
    rate_per_s: float = 1.0

    def __post_init__(self):
        self._lock = threading.Lock()
        self._last = 0.0

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            delta = now - self._last
            min_interval = 1.0 / self.rate_per_s
            if delta < min_interval:
                time.sleep(min_interval - delta)
            self._last = time.monotonic()


ARXIV_LIMITER = SimpleRateLimiter(rate_per_s=1.0)
