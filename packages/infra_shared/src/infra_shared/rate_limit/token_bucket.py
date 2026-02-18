import time
from threading import Lock


class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.timestamp
            self.timestamp = now

            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate,
            )

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False
