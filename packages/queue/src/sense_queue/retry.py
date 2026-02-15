from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    base_delay_s: float = 0.5
    max_delay_s: float = 30.0
    backoff_factor: float = 2.0

    def should_retry(self, *, attempt: int) -> bool:
        """
        attempt is 1-based (attempt=1 means first failure).
        """
        return attempt <= self.max_retries

    def next_delay_s(self, *, attempt: int) -> float:
        """
        Exponential backoff delay for a given attempt (1-based).
        """
        exp = self.base_delay_s * (self.backoff_factor ** max(0, attempt - 1))
        return min(self.max_delay_s, exp)
