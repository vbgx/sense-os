from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3

    def should_retry(self, *, attempt: int) -> bool:
        """
        attempt is 1-based (attempt=1 means first failure).
        """
        return attempt <= self.max_retries
