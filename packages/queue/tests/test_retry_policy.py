from __future__ import annotations

from sense_queue.retry import RetryPolicy


def test_retry_policy_default_3():
    p = RetryPolicy()
    assert p.should_retry(attempt=1) is True
    assert p.should_retry(attempt=2) is True
    assert p.should_retry(attempt=3) is True
    assert p.should_retry(attempt=4) is False


def test_retry_policy_backoff_growth():
    p = RetryPolicy(max_retries=5, base_delay_s=1.0, backoff_factor=2.0, max_delay_s=5.0)
    assert p.next_delay_s(attempt=1) == 1.0
    assert p.next_delay_s(attempt=2) == 2.0
    assert p.next_delay_s(attempt=3) == 4.0
    assert p.next_delay_s(attempt=4) == 5.0
