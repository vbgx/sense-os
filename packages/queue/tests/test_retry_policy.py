from __future__ import annotations

from sense_queue.retry import RetryPolicy


def test_retry_policy_default_3():
    p = RetryPolicy()
    assert p.should_retry(attempt=1) is True
    assert p.should_retry(attempt=2) is True
    assert p.should_retry(attempt=3) is True
    assert p.should_retry(attempt=4) is False
